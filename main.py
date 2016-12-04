#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
from google.appengine.ext.webapp import template
import logging
from google.appengine.ext import ndb
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/category"))


class Image(ndb.Model):
    image_path = ndb.StringProperty()


class Entry(ndb.Model):
    name = ndb.StringProperty()
    content = ndb.TextProperty()
    tags = ndb.KeyProperty(repeated=True)
    post_path = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    images = ndb.KeyProperty(kind=Image, repeated=True)


class Tag(ndb.Model):
    content = ndb.StringProperty()

    @property
    def entries(self):
        return Entry.gql("WHERE tags = :1", self.key())


defined_list_of_tags = ['drawings', 'code', 'interactive', 'comics', 'paintings']

class MainHandler(webapp2.RequestHandler):
    def get(self):
        for tag in defined_list_of_tags:
            q = Tag.query(Tag.content == tag)
            if len(q.fetch()) <= 0:
                new_tag = Tag(content=tag)
                new_tag.put()
        temp = os.path.join(os.path.dirname(__file__),
                            'index.html')
        outstr = template.render(temp,
                                 {'title': 'Thao Huong\' Portfolio'})
        self.response.write(outstr)


class ErrorHandler(webapp2.RequestHandler):
    def get(self):
        temp = os.path.join(os.path.dirname(__file__),
                            'index.html')
        outstr = template.render(temp,
                                 {})
        self.response.write(outstr)


class CategoryHandler(webapp2.RequestHandler):
    def get(self):
        # Get tag name from path
        path = self.request.path
        locate = path.find('category') + 9
        name = path[locate:]
        logging.info('look for category page: ' + name)
        # Search tags by tag name
        q = Tag.query(Tag.content == name)
        tag_list = q.fetch()
        if len(tag_list) > 0:
            # Filter entries by tag key
            entry_q = Entry.query(Entry.tags.IN([tag_list[0].key]))
            gallery_items = entry_q.fetch()
            for gallery_item in gallery_items:
                image_q = Image.query(Image.key == gallery_item.images[0])
                image_results = image_q.fetch()
                image_path = image_results[0].image_path
                gallery_item.image_path = image_path
                if len(gallery_item.content) > 300:
                    first_para_index = gallery_item.content.find('</p>') + 4
                    if first_para_index == 3:
                        first_para_index = gallery_item.content.find('\n')
                    if first_para_index == -1:
                        first_para_index = gallery_item.content.find('<br>') + 4
                    if first_para_index == 3:
                        first_para_index = len(gallery_item.content)
                    gallery_item.content = gallery_item.content[:first_para_index] + "..."
            template_vars = {'category': name.lower(), 'title': name.upper(), 'page_title': name.upper(), 'gallery_items': gallery_items}
            temp = JINJA_ENVIRONMENT.get_template('/category-base.html')
            self.response.out.write(temp.render(template_vars))
        else:
            temp = os.path.join(os.path.dirname(__file__),
                                'index.html')
            outstr = template.render(temp,
                                     {'title': 'Thao Huong\' Portfolio'})
            self.response.write(outstr)


class AboutHandler(webapp2.RequestHandler):
    def get(self):
        template_vars = {'category': 'about', 'title': 'About', 'page_title': 'ABOUT'}
        template = JINJA_ENVIRONMENT.get_template('about.html')
        self.response.out.write(template.render(template_vars))


class ResumeHandler(webapp2.RequestHandler):
    def get(self):
        template_vars = {'category': 'resume', 'title': 'Resume', 'page_title': 'RESUME'}
        template = JINJA_ENVIRONMENT.get_template('resume.html')
        self.response.out.write(template.render(template_vars))


class ItemHandler(webapp2.RequestHandler):
    def get(self):
        path = self.request.path
        locate = path.find('item') - 1
        name = path[locate:]
        logging.info('look for path: ' + name)
        q = Entry.query(Entry.post_path == name)
        results = q.fetch()
        logging.info('path results is: ' + str(results))
        if len(results) > 0:
            entry = results[0]
            logging.info('entry results is: ' + str(entry))
            image_paths = []
            # CHANGE BACK TO SKIP = FALSE!!!!
            skip = False
            for image_key in entry.images:
                if not skip:
                    skip = True
                    continue
                image_q = Image.query(Image.key == image_key)
                image_results = image_q.fetch()
                logging.info('image query results is: ' + str(image_results))
                image_path = image_results[0].image_path
                image_paths.append(image_path)
            template_vars = {'page_title': entry.name, 'image_paths': image_paths, 'description': entry.content, 'title': entry.name}
            temp = JINJA_ENVIRONMENT.get_template('/item-base.html')
            self.response.out.write(temp.render(template_vars))
        else:
            temp = os.path.join(os.path.dirname(__file__),
                                'index.html')
            outstr = template.render(temp,
                                     {'title': 'Thao Huong\' Portfolio'})
            self.response.write(outstr)


class NewEntryHandler(webapp2.RequestHandler):
    def get(self):
        temp = os.path.join(os.path.dirname(__file__),
                            'new-entry.html')
        outstr = template.render(temp,
                                 {})
        self.response.write(outstr)

    def post(self):
        name = self.request.get('name')
        content = self.request.get('content')
        post_path = self.request.get('post-path')
        entry = Entry(content=content, name=name, post_path=post_path)
        tags = {}
        images = []
        for i in range(1, 6):
            tag_string = self.request.get('tag' + str(i))
            if len(tag_string) > 0:
                q = Tag.query(Tag.content == tag_string)
                tag_list = q.fetch()
                logging.info("results of tag query is " + str(tag_list))
                tag = tag_list[0]
                entry.tags.append(tag.key)

        for i in range(1, 9):
            image_string = self.request.get('image-path' + str(i))
            if len(image_string) > 0:
                images.append(image_string)

        for image_path in images:
            image = Image(image_path=image_path)
            image.put()
            logging.info("image is " + str(image))
            logging.info("image.key is " + str(image.key))
            logging.info("images of entry is " + str(entry.images))
            logging.info("entry is " + str(entry))
            entry.images.append(image.key)
            logging.info("images of entry after append is " + str(entry.images))
        # for tag in tags:
        #     if tag not in entry.tags:
        #         logging.info("tag is " + str(tag))
        #         entry.tags.append(tag)
        # entry.thumbnail_path = 'images/cornell_college.jpg'
        entry.put()
        temp = os.path.join(os.path.dirname(__file__),
                            'new-entry.html')
        outstr = template.render(temp,
                                 {})
        self.response.write(outstr)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/category/.*', CategoryHandler),
    ('/about', AboutHandler),
    ('/item/.*', ItemHandler),
    #('/new-entry', NewEntryHandler),
    ('/resume', ResumeHandler),
    ('/.*', ErrorHandler),
], debug=True)
