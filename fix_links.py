# Copyright (C) 2025 Twitchy Ears.
#
# This file is NOT part of rss2email but is intended for use with it.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see
# <https://www.gnu.org/licenses/>.

"""Small function to include images inline in emails from mastodon RSS feeds

Set: 
post-process = fix_links process

Read pretty.py for more examples, this is cribbed from there.

add_links
  a filter that adds the links back in

process
  the actual post_process function that you need to call in
  the config file
"""


# import modules you need
from bs4 import BeautifulSoup
import textwrap
import rss2email.email

def add_links(feed, parsed, entry, guid, message):
    """Use BeautifulSoup and the json parser to add links back in

    Reads the entry JSON data blob and if it finds media_content it
    attempts to BeautifulSoup it back into the message object at the
    bottom of the body div as direct img links before returning the
    reconstructed message.

    """
    # decode message
    encoding = message.get_charsets()[0]
    
    if (encoding is None):
        encoding = 'us-ascii'
    
    msg_content = str(message.get_payload(decode=True), encoding)

    # modify content
    soup = BeautifulSoup(msg_content, 'html.parser')

    # For debugging purposes
    # 
    # content = soup.prettify()
    # dump_file = "/tmp/dump_file.fix_links"
    # with open(dump_file, 'a') as text_file:
    #     text_file.write(f"\n\n----- PARSED -----\n\n{parsed}")
    #     text_file.write(f"\n\n----- ENTRY -----\n\n{entry}")
    #     text_file.write(f"\n\n----- CONTENT -----\n\n{content}")
    #     text_file.write(f"\n\n----- END OF pretty()      ------\n\n")

    # print(entry)
    # print(soup.prettify())

    # Something is generating pointless spans
    for tag in soup.find_all('span'):
        tag.unwrap()

    body_div = soup.find(id = "body")

    # If we have some media content
    if ('media_content' in entry):

        # Run through them
        for i in (range(0, len(entry.media_content))): 
            media_content = entry.media_content[i]
            content = None

            # Extract content, which contains alt_text if exists, its
            # another JSON structure with matching elements (so
            # media_content[3] has alt text in content[3] for example)
            if ('content' in entry and i < len(entry.content)):
                content = entry.content[i]

            # If we have images with URLs
            if ("medium" in media_content
                and media_content["medium"] == "image"
                and "url" in media_content):
                
                    url = media_content["url"]
                    alt_text = url

                    # Get the associated alt text
                    if (content is not None
                        and "type" in content
                        and content["type"] == "text/plain"
                        and "value" in content):
                
                        alt_text = content["value"]

                    # Create a div that contains the img and alt text
                    # below in a p tag
                    container = soup.new_tag('div')
                    img_tag = soup.new_tag('img')
                    img_tag.attrs["src"] = url
                    alt_p = soup.new_tag('p')
                    alt_p.string = alt_text

                    container.append(img_tag)
                    container.append(alt_p)

                    body_div.append(container)



    # Dump it back out - need some kind of wrapping
    wrapper = textwrap.TextWrapper(width = 998, replace_whitespace = False)
    soup_dump = wrapper.fill(text = soup.prettify(formatter="minimal"))
    msg_content = soup_dump


    # And now we're back to the original pretty.py
    
    # BeautifulSoup uses unicode, so we perhaps have to adjust the encoding.
    # It's easy to get into encoding problems and this step will prevent
    # them ;)
    encoding = rss2email.email.guess_encoding(msg_content, encodings=feed.encodings)

    # clear CTE and set message. It can be important to clear the CTE
    # before setting the payload, since the payload is only re-encoded
    # if CTE is not already set.
    del message['Content-Transfer-Encoding']
    message.set_payload(msg_content, charset=encoding)
    return message


def process(feed, parsed, entry, guid, message):
    message = add_links(feed, parsed, entry, guid, message)
    # you could add several filters in here if you want to

    # we need to return the message, if we return False,
    # the feed item will be skipped
    return message
