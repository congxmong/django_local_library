from django.shortcuts import render, get_object_or_404
from catalog.models import Book, Author, BookInstance, Genre, Language
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
# from catalog.forms import RenewBookForm
from catalog.forms import RenewBookModelForm
from django.contrib.auth.decorators import permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


# Create your views here.
def index(request):
    """View function for home page of site"""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default
    num_authors = Author.objects.count()

    num_genres = Genre.objects.count()

    num_languages = Language.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_languages': num_languages,
        'num_visits': num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    # max number of book in a paginate
    paginate_by = 10
    context_object_name = 'my_book_list'  # your own name for the list as a template variable
    queryset = Book.objects.filter(title__icontains='sea')[:5]  # Get 5 books containing the title sea
    template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location

    def get_queryset(self):
        # return Book.objects.filter(title__icontains='sea')[:5] # Get 5 books containing the title sea
        return Book.objects.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10
    context_object_name = 'my_author_list'
    # template_name = 'authors/my_arbitrary_template_name_list.html'

    def get_queryset(self):
        return Author.objects.all()

    # def get_context_data(self, **kwargs):
    #     context = super(AuthorListView, self).get_context_data(**kwargs)
    #     context['some_data'] = 'This is just some data'
    #     return context


class BookDetailView(generic.DetailView):
    model = Book

    def book_detail_view(request, primary_key):
        book = get_object_or_404(Book, pk=primary_key)
        return render(request, 'catalog/book_detail.html', context={'book': book})

class AuthorDetailView(generic.DetailView):
    model = Author

    def author_detail_view(request, primary_key):
        author = get_object_or_404(Author, pk=primary_key)
        return render(request, 'catalog/author_detail.html', context={'author': author})


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrowed=self.request.user).filter(status__exact='o').order_by('due_back')


class MyView(PermissionRequiredMixin, generic.View):
    permission_required = 'catalog.can_mark_returned'
    # Or multiple permissions
    permission_required = ('catalog.can_mark_returned', 'catalog.can_edit')
    # Note that 'catalog.can_edit' is just an example
    # the catalog application doesn't have such permission!


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        # form = RenewBookForm(request.POST)
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            # book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('my-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        # form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    # initial = {'date_of_death': '05/01/2018'}
    success_url = reverse_lazy('authors')


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

    def get_success_url(self):
        companyid = self.kwargs['pk']
        return reverse_lazy('author-detail', kwargs={'pk': companyid})

    # success_url = reverse_lazy('author_update')


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    success_url = reverse_lazy('books')


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'

    def get_success_url(self):
        bookid = self.kwargs['pk']
        return reverse_lazy('book-detail', kwargs={'pk': bookid})


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')


class BookInstanceCreate(CreateView):
    model = BookInstance
    fields = '__all__'
    success_url = reverse_lazy('books')
