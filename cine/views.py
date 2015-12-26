from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.base import RedirectView

from .models import Adress, Cinephile, DispoToWatch, Film, Soiree, Vote


class CinephileRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return Cinephile.objects.filter(user=self.request.user).exists()


class VotesView(CinephileRequiredMixin, UpdateView):  # TODO: this is a PoC… clean it.
    def post(self, request, *args, **kwargs):
        ordre = request.POST['ordre'].split(',')
        if ordre:
            request.user.cinephile.votes.clear()
            films = [get_object_or_404(Film, slug=slug, vu=False) for slug in ordre if slug]
            for film in films:
                request.user.cinephile.votes.add(film)
            request.user.cinephile.save()
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, 'cine/votes.html', {
            'films': request.user.cinephile.votes.all(),
            'films_pas_classes': request.user.cinephile.pas_classes(),
            })


class ICS(ListView):
    template_name = 'cine/cinenim.ics'
    content_type = "text/calendar; charset=UTF-8"
    model = Soiree


class FilmActionMixin(CinephileRequiredMixin):
    model = Film
    fields = ('titre', 'description', 'annee_sortie', 'titre_vo', 'realisateur', 'imdb', 'allocine', 'duree', 'imdb_poster_url', 'imdb_id')

    def form_valid(self, form):
        messages.info(self.request, "Film %s" % self.action)
        return super(FilmActionMixin, self).form_valid(form)


class FilmCreateView(FilmActionMixin, CreateView):
    action = "créé"

    def form_valid(self, form):
        form.instance.respo = self.request.user
        return super(FilmCreateView, self).form_valid(form)

    def get_initial(self):
        return Film.get_imdb_dict(self.request.GET.get('imdb_id'))


class FilmUpdateView(FilmActionMixin, UpdateView):
    action = "modifié"

    def form_valid(self, form):
        if form.instance.respo == self.request.user or self.request.user.is_superuser:
            return super(FilmUpdateView, self).form_valid(form)
        messages.error(self.request, 'Vous n’avez pas le droit de modifier ce film')
        return redirect('cine:films')


class FilmListView(ListView):
    model = Film


class FilmVuView(UserPassesTestMixin, RedirectView):
    def test_func(self):
        return self.request.user.is_superuser

    def get_redirect_url(self, *args, **kwargs):
        film = get_object_or_404(Film, slug=kwargs['slug'])
        film.vu = True
        film.vote_set.update(choix=-1, veto=False)
        film.save()
        return reverse('cine:films')


class VetoView(CinephileRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        vote = get_object_or_404(Vote, pk=kwargs['pk'])
        vote.veto = True
        vote.choix = -1
        vote.save()
        return reverse('cine:votes')


class CinephileListView(CinephileRequiredMixin, ListView):
    queryset = User.objects.filter(groups__name='cine')
    template_name = 'cine/cinephile_list.html'


class SoireeCreateView(CinephileRequiredMixin, CreateView):
    model = Soiree
    fields = ['date', 'time']

    def form_valid(self, form):
        form.instance.hote = self.request.user
        messages.info(self.request, "Soirée Créée")
        return super(SoireeCreateView, self).form_valid(form)

    def get_success_url(self):
        if self.object.has_adress():
            return reverse('cine:home')
        return reverse('cine:adress')


class DTWUpdateView(CinephileRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        dtw = get_object_or_404(DispoToWatch, soiree__pk=kwargs['pk'], cinephile=request.user)
        if request.user == dtw.soiree.hote and kwargs['dispo'] != 'O':
            messages.error(request, "Oui, mais non. Si tu crées une soirée, tu y vas.")
            return redirect('cine:home')
        dtw.dispo = kwargs['dispo']
        dtw.save()
        messages.info(request, "Disponibilité mise à jour !")
        return redirect('cine:home')


class AdressUpdateView(CinephileRequiredMixin, UpdateView):
    fields = ['adresse']
    success_url = reverse_lazy('cine:home')

    def get_object(self, queryset=None):
        return Adress.objects.get_or_create(user=self.request.user)[0]

    def form_valid(self, form):
        messages.info(self.request, "Adresse mise à jour")
        return super(AdressUpdateView, self).form_valid(form)
