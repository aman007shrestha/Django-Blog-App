from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, Like
from django.views.generic import (
	ListView, 
	DetailView,
	CreateView, 
	UpdateView,
	DeleteView
	)

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import CommentForm
from django.urls import reverse_lazy
from django.views import View


from django.db.models import Q

# for pagination bits 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def home(request):
	posts = Post.objects.all()
	for post in posts:
		post.number_of_comments = post.comments.all().count()
		print(post.number_of_comments)
	context = {
		'posts': posts
	}
	return render(request, 'blog/home.html', context)


class PostListView(ListView):
	model = Post
	template_name = 'blog/home.html'
	context_object_name = 'posts'
# if my view only had a Generic paginate_by = 2 should do the task 
# since it also has a functional bits 
# we went via the functional pagination 

	def get(self, request):
		likes = list()
		posts = Post.objects.order_by('-date_posted')
		#  set the page attribute to 1 if none
		# page attribute is passed via get method 
		page = request.GET.get('page', 1)
		# set paginator object num_of objects in each page=5
		paginator = Paginator(posts, 5)
		# paginating our post_list
		try:
			posts = paginator.page(page)
		# url..?page=some-random-strin
		# this wil actualy return result same as page=1 
		# because of excepption handling
		except PageNotAnInteger:
			posts = paginator.page(1)
		# consider the user want to query page > num_pages as
		# ?page={{ some_num>num_pages }} which is empty 
		# in this case our exception handles to return to the last
		except EmptyPage:
			posts = paginator.page(paginator.num_pages)

		# exceptions handling for pagination

		for post in posts:
			post.number_of_comments = post.comments.all().count()
			post.number_of_likes = post.likes.all().count()
		print(post.number_of_comments)
		if request.user.is_authenticated:
			# get a list of liked post of current logged in user
			rows = request.user.post_likes.values('id')
			likes = [row['id'] for row in rows]
		self.paginate_by = 3
		context = {
			'posts': posts,
			"likes": likes
		}
		return render(request, self.template_name, context)


class PostDetailView(DetailView):
	model = Post
	template_name = 'blog/post_detail.html'
	# extend get method to include comments
	def get(self, request, pk):
		post_object = get_object_or_404(self.model, id=pk)
		comments = Comment.objects.filter(post=post_object).order_by('-updated_at')
		comment_form  = CommentForm()
		context = {
			'post':post_object,
			'comments': comments,
			'comment_form':comment_form
		}
		return render(request, self.template_name, context)

	
class PostCreateView(LoginRequiredMixin ,CreateView):
	model = Post
	fields = ['title', 'content']

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin,UpdateView):
	model = Post
	fields = ['title', 'content']

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super().form_valid(form)

	def test_func(self):
		post = self.get_object()
		if self.request.user == post.author:
			return True
		return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = Post
	success_url = '/'
	
	def test_func(self):
		post = self.get_object()
		if self.request.user == post.author:
			return True
		return False


# the view allows user to store a comment
class CommentCreateView(LoginRequiredMixin, View):
	model = Comment
	def post(self, request, pk):
		post = get_object_or_404(Post, id=pk)
		comment = Comment(text=request.POST['comment'], author=request.user, post=post)
		comment.save()
		return redirect(reverse('post-detail', args=[pk]))


# extends delete view with owner capability
class CommentDeleteView(DeleteView):
	model = Comment
	# method to check owner
	def get_queryset(self):
		qs = super(CommentDeleteView, self).get_queryset()
		query = Q(author=self.request.user)
		query.add(Q(post__author = self.request.user), Q.OR)
		return qs.filter(query)

	def get_success_url(self):
		post = self.object.post
		return reverse('post-detail', args=[post.id])


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name="dispatch")
class PostLikeView(LoginRequiredMixin, View):
	def post(self, request, pk):
		post = get_object_or_404(Post, id=pk)
		like_obj = Like(author=request.user, post=post)
		try:
			like_obj.save()
		except IntegrityError as e:
			pass
		return HttpResponse()

@method_decorator(csrf_exempt, name="dispatch")
class DeleteLikeView(LoginRequiredMixin, View):
	def post(self, request, pk):
		post = get_object_or_404(Post, id=pk)
		try:
			Like.objects.get(author=request.user, post=post).delete()
		except Like.DoesNotExist as e:
			pass
		return HttpResponse()



def about(request):

	return render(request, 'blog/about.html', {'title': "About"})

	
class UserPostListView(ListView):
	model = Post
	template_name = 'blog/user_posts.html'


	def get(self, request, username):
		likes = list()
		user = get_object_or_404(User, username=username)
		posts = Post.objects.filter(author=user).order_by('-date_posted')
		#  set the page attribute to 1 if none
		# page attribute is passed via get method 
		page = request.GET.get('page', 1)
		# set paginator object num_of objects in each page=5
		paginator = Paginator(posts, 5)
		# paginating our post_list
		try:
			posts = paginator.page(page)
		# url..?page=some-random-strin
		# this wil actualy return result same as page=1 
		# because of excepption handling
		except PageNotAnInteger:
			posts = paginator.page(1)
		# consider the user want to query page > num_pages as
		# ?page={{ some_num>num_pages }} which is empty 
		# in this case our exception handles to return to the last
		except EmptyPage:
			posts = paginator.page(paginator.num_pages)

		# exceptions handling for pagination

		for post in posts:
			post.number_of_comments = post.comments.all().count()
			post.number_of_likes = post.likes.all().count()
		print(post.number_of_comments)
		if request.user.is_authenticated:
			# get a list of liked post of current logged in user
			rows = request.user.post_likes.values('id')
			likes = [row['id'] for row in rows]
		self.paginate_by = 3
		context = {
			'username': username,
			'posts': posts,
			"likes": likes
		}
		return render(request, self.template_name, context)

