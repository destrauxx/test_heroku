from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
import os
from PIL import Image
from io import BytesIO
# Create your models here.

User = settings.AUTH_USER_MODEL


class Commentaries(models.Model):
    class Meta:
        ordering = ['-date']
        
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField(blank=False, null=True)

    
class Likes(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    like = models.BooleanField(default=False)

class News(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    article = models.CharField(max_length=100)
    body = models.TextField(blank=False, null=False)
    commentary = models.ManyToManyField(Commentaries)
    likes = models.ManyToManyField(Likes)
    image = models.ImageField(upload_to='news_images/', default='news_images/default_news.jpg',)
    image_thumbnail = models.ImageField(upload_to='news_images/',default='news_images/default_news_thumb.jpg', null=True, blank=True)
    def __str__(self):
        return self.article

    def get_likes(self):
        return self.likes.count()
    
    def get_comments_counter(self):
        return self.commentary.count()
    
    def get_image_name(self):
        return self.image if self.image else False

    def make_thumbnail(self):
        image = Image.open(self.image)
        image.thumbnail((100, 100), Image.ANTIALIAS)
        thumb_name, thumb_extension = os.path.splitext(self.image.name)
        thumb_extension = thumb_extension.lower()
        thumb_filename = thumb_name.split('/')[0] + '_thumb' + thumb_extension

        if thumb_name == 'news_images/default_news':
            return
        if thumb_extension in ['.jpg', '.jpeg']:
            FILE_TYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FILE_TYPE = 'GIF'
        elif thumb_extension == '.png':
            FILE_TYPE = 'PNG'
        temp_thumb = BytesIO()
        image.save(temp_thumb, FILE_TYPE)
        temp_thumb.seek(0)
        self.image_thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        
    
    def save(self, *args, **kwargs):
        self.make_thumbnail()
        super(News, self).save(*args, **kwargs)
    



