"""Premailer for emencia.django.newsletter
Used for converting a page with CSS inline and links corrected.
Based on http://www.peterbe.com/plog/premailer.py"""
import re
from urllib2 import urlopen
from lxml.html import parse
from lxml.html import tostring


_css_comments = re.compile(r'/\*.*?\*/', re.MULTILINE | re.DOTALL)
_regex = re.compile('((.*?){(.*?)})', re.DOTALL | re.M)
_semicolon_regex = re.compile(';(\s+)')
_colon_regex = re.compile(':(\s+)')


def _merge_styles(old, new, class_=''):
    """
    if ::
      old = 'font-size:1px; color: red'
    and ::
      new = 'font-size:2px; font-weight: bold'
    then ::
      return 'color: red; font-size:2px; font-weight: bold'

    In other words, the new style bits replace the old ones.

    The @class_ parameter can be something like ':hover' and if that
    is there, you split up the style with '{...} :hover{...}'
    Note: old could be something like '{...} ::first-letter{...}'
    """
    news = {}
    for k, v in [x.strip().split(':', 1) for x in new.split(';') if x.strip()]:
        news[k.strip()] = v.strip()

    groups = {}
    grouping_regex = re.compile('([:\-\w]*){([^}]+)}')
    grouped_split = grouping_regex.findall(old)
    if grouped_split:
        for old_class, old_content in grouped_split:
            olds = {}
            for k, v in [x.strip().split(':', 1)
                         for x in old_content.split(';') if x.strip()]:
                olds[k.strip()] = v.strip()
            groups[old_class] = olds
    else:
        olds = {}
        for k, v in [x.strip().split(':', 1)
                     for x in old.split(';') if x.strip()]:
            olds[k.strip()] = v.strip()
        groups[''] = olds

    # Perform the merge
    merged = news
    for k, v in groups.get(class_, {}).items():
        if k not in merged:
            merged[k] = v
    groups[class_] = merged

    if len(groups) == 1:
        return '; '.join(['%s:%s' % (k, v)
                          for (k, v) in groups.values()[0].items()])
    else:
        all = []
        for class_, mergeable in sorted(groups.items(),
                                        lambda x, y: cmp(x[0].count(':'), y[0].count(':'))):
            all.append('%s{%s}' % (class_,
                                   '; '.join(['%s:%s' % (k, v)
                                              for (k, v)
                                              in mergeable.items()])))
        return ' '.join([x for x in all if x != '{}'])


class PremailerError(Exception):
    pass


class Premailer(object):
    """Premailer for converting a webpage
    to be e-mail ready"""

    def __init__(self, url, include_star_selectors=False):
        self.url = url
        try:
            self.page = parse(self.url).getroot()
        except:
            raise PremailerError('Could not parse the html')

        self.include_star_selectors = include_star_selectors

    def transform(self):
        """Do some transformations to self.page
        for being e-mail compliant"""
        self.page.make_links_absolute(self.url)

        self.inline_rules(self.get_page_rules())
        self.clean_page()
        # Do it a second time for correcting
        # ressources added by inlining.
        # Will not work as expected if medias
        # are located in other domain.
        self.page.make_links_absolute(self.url)

        return tostring(self.page.body)

    def get_page_rules(self):
        """Retrieve CSS rules in the <style> markups
        and in the external CSS files"""
        rules = []
        for style in self.page.cssselect('style'):
            css_body = tostring(style)
            css_body = css_body.split('>')[1].split('</')[0]
            these_rules, these_leftover = self._parse_style_rules(css_body)
            rules.extend(these_rules)

        for external_css in self.page.cssselect('link'):
            attr = external_css.attrib
            if attr.get('rel', '').lower() == 'stylesheet' and \
                   attr.get('href'):
                media = attr.get('media', 'screen')
                for media_allowed in ('all', 'screen', 'projection'):
                    if media_allowed in media:
                        css = urlopen(attr['href']).read()
                        rules.extend(self._parse_style_rules(css)[0])
                        break

        return rules

    def inline_rules(self, rules):
        """Apply in the page inline the CSS rules"""
        for selector, style in rules:
            class_ = ''
            if ':' in selector:
                selector, class_ = re.split(':', selector, 1)
                class_ = ':%s' % class_

            for item in self.page.cssselect(selector):
                old_style = item.attrib.get('style', '')
                new_style = _merge_styles(old_style, style, class_)
                item.attrib['style'] = new_style
                self._style_to_basic_html_attributes(item, new_style)

    def clean_page(self):
        """Clean the page of useless parts"""
        for elem in self.page.xpath('//@class'):
            parent = elem.getparent()
            del parent.attrib['class']
        for elem in self.page.cssselect('style'):
            elem.getparent().remove(elem)
        for elem in self.page.cssselect('script'):
            elem.getparent().remove(elem)

    def _parse_style_rules(self, css_body):
        leftover = []
        rules = []
        css_body = _css_comments.sub('', css_body)
        for each in _regex.findall(css_body.strip()):
            __, selectors, bulk = each
            bulk = _semicolon_regex.sub(';', bulk.strip())
            bulk = _colon_regex.sub(':', bulk.strip())
            if bulk.endswith(';'):
                bulk = bulk[:-1]
            for selector in [x.strip()
                             for x in selectors.split(',') if x.strip()]:
                if ':' in selector:
                    # A pseudoclass
                    leftover.append((selector, bulk))
                    continue
                elif selector == '*' and not self.include_star_selectors:
                    continue

                rules.append((selector, bulk))

        return rules, leftover

    def _style_to_basic_html_attributes(self, element, style_content):
        """Given an element and styles like
        'background-color:red; font-family:Arial' turn some of that into HTML
        attributes. like 'bgcolor', etc.
        Note, the style_content can contain pseudoclasses like:
        '{color:red; border:1px solid green} :visited{border:1px solid green}'
        """
        if style_content.count('}') and \
          style_content.count('{') == style_content.count('{'):
            style_content = style_content.split('}')[0][1:]

        attributes = {}
        for key, value in [x.split(':') for x in style_content.split(';')
                           if len(x.split(':')) == 2]:
            key = key.strip()

            if key == 'text-align':
                attributes['align'] = value.strip()
            elif key == 'background-color':
                attributes['bgcolor'] = value.strip()
            elif key == 'width':
                value = value.strip()
                if value.endswith('px'):
                    value = value[:-2]
                attributes['width'] = value

        for key, value in attributes.items():
            if key in element.attrib:
                # Already set, don't dare to overwrite
                continue
            element.attrib[key] = value
