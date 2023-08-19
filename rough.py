# I used this python file to programatically edit html files (changing src and href attributes) and also used this file
# as rough coding (testing my code before writting it in my main backend file)

import os

listOfFiles = os.listdir('templates')

def convert_to_endpoint(phpfilename):
    if 'index' in phpfilename:
        return ""
    else:
        return phpfilename.split('.')[0].replace('-', '_')
    
def append_at_top(filepath, text):
    with open(filepath, 'r+') as f:
        content = f.read()
        content = text + content
        f.seek(0)
        f.write(content)

# for filename in listOfFiles:
#     index = listOfFiles.index(filename)
#     listOfFiles[index] = filename.replace('html', 'php')

for filename in listOfFiles:
    # complete_filename = 'templates/' + filename.split('.')[0] + '.html'
    complete_filename = 'templates/' + filename
    text = "{% extends 'base.html' %}\n{% block mainslider %} {% endblock mainslider %}\n"
    append_at_top(complete_filename, text=text)
    # with open('test.txt', 'r+') as f:
    
        # content = f.read()
        # for linkfilename in listOfFiles:
        # endpoint = convert_to_endpoint(linkfilename)
        # content = content.replace('href="assets', f'href="static/assets')
        # content = content.replace('scr="assets', f'src="static/assets')
        # content = content.replace('<a href="team.php', '<a href="/team-details')
        # content = content.replace('<a href="/team-details', '<a href="/team')
        # content = content.replace('url(assets/', 'url(/static/assets/')
        # content = content.replace('href="d', 'href="/static/d')
        
        # f.seek(0)
        # f.write('''
        #         {% extends 'base.html' %}

        #         {% block mainslider %} {% endblock mainslider %}\n
        #     ''')
        # print(f'Modified {filename}')

    # with open(complete_filename, 'wt') as f:
    #     f.write(content)
    #     print(f'{filename} modified successfully')

