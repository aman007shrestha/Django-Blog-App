from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinLengthValidator
from django.conf import settings
# Create your models here.


class Post(models.Model):
	title = models.CharField(max_length=100)
	content = models.TextField()
	
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	comments = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Comment",
	 related_name="post_comments")
	likes = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Like',
		related_name='post_likes')
	date_posted = models.DateTimeField(default=timezone.now)
	date_updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('post-detail', kwargs={'pk':self.pk})


class Comment(models.Model):
	text = models.TextField(
		validators=[MinLengthValidator(2, "Atleast 2 characters")]
		)
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		if len(self.text) < 15:
			return self.text
		else:
			return self.text[:12] + '...'

class Like(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	class Meta:
		unique_together = ('post', 'author')

	def __str__(self):
		return "%s likes %s"(self.author.username, self.post.title[:10])