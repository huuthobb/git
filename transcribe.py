from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pydub import AudioSegment
import time, os, shutil


def expand_shadow_element(element):
    shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
    return shadow_root

# Cut audio file
# AudioSegment.converter = r"F:\PY\ffmpeg\bin"
# AudioSegment.ffmpeg = r"F:\PY\ffmpeg\bin"

'''
# Make temp dir
path = os.path.join(os.getcwd(),'temp')
if not(os.path.isdir(path)):
    os.mkdir(path,755)
tempfile.tempdir = os.getcwd() + '\\temp'
print(tempfile.gettempdir())
'''
path = os.path.join(os.getcwd(), 'audiocut')
try:
    os.mkdir(path)
except:
    pass
for file in os.listdir(os.getcwd()):
    if file.endswith('.mp3'):
        file_mp3 = file
song = AudioSegment.from_mp3(file_mp3)
start_cut = 0
end_cut = 30000
count = 1
# clear = lambda: os.system('cls')
print('Analysing audio file...')
while end_cut <= len(song):
    #clear()
    print('Processing '+str(round((end_cut/1000)/song.duration_seconds*100))+'%', end='\r')
    file_cut = song[start_cut:end_cut]
    file_cut.export(path+'\\'+str(count)+'.mp3', format='mp3')
    if (end_cut == len(song)):
        break
    elif ((end_cut + 30000) > len(song)):
        start_cut = end_cut
        end_cut = len(song)
    else:
        start_cut = end_cut
        end_cut += 30000
    count += 1
print('')
print('DONE')

# Open browser
url = 'https://cloud.google.com/speech-to-text/'

driver = webdriver.Chrome('chromedriver.exe')
driver.get(url)

print('Choosing language Vietnamese ...')
# Choose language Vietnamese
try:
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.ID,'streaming_demo_section')))
finally:
    driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))
    root1 = driver.find_element_by_tag_name('sp-app')
    shadow_root1 = expand_shadow_element(root1)
    root2 = shadow_root1.find_element_by_tag_name('sp-controls')
    shadow_root2 = expand_shadow_element(root2)
    language = shadow_root2.find_elements_by_tag_name('paper-item')
    driver.execute_script("arguments[0].click()", language[85])
print('DONE')

print('Please input CAPTCHA to transcribe audio file ...')


string = ""
wait_capcha = True
for i in range(count):
    #Choose file to transcribe
    shadow_root2.find_element_by_id('fileInput').send_keys(path+'\\'+str(i+1)+'.mp3')

    while wait_capcha:
        time.sleep(5)
        print('Still wait CAPTCHA ...')
        capcha = driver.find_elements_by_tag_name('div')
        try:
            if capcha[2].get_attribute('hidden') == 'true':
                wait_capcha = False
                driver.set_window_position(-10000, 0)
                print('DONE')
                print('Transcribing audio file ...')
        except:
            pass

    # Wait to transcribe
    wait = True
    while wait:
        time.sleep(5)
        root1 = driver.find_element_by_tag_name('sp-app')
        shadow_root1 = expand_shadow_element(root1)
        root2 = shadow_root1.find_element_by_tag_name('sp-controls')
        shadow_root2 = expand_shadow_element(root2)
        content = shadow_root2.get_attribute('innerHTML')
        soup = BeautifulSoup(content, 'html.parser')
        loading = soup.find('div', {'class': 'container loading'})
        try:
            if (loading['style']=='display: none;'):
                wait = False
        except KeyError:
            pass

    # Get text
    root1 = driver.find_element_by_tag_name('sp-app')
    shadow_root1 = expand_shadow_element(root1)
    root3 = shadow_root1.find_element_by_tag_name('sp-results')
    shadow_root3 = expand_shadow_element(root3)
    text_zone = shadow_root3.find_element_by_class_name('iron-selected')
    texts = text_zone.find_elements_by_tag_name('sp-word')
    for text in texts:
        expand_text = expand_shadow_element(text)
        string = string + expand_text.find_element_by_tag_name('span').text + " "
    string += "\n"
    print('Processing '+str(round((i+1)/count*100))+'%', end='\r')
print('')
print('COMPLETE!')

# Close browser
driver.quit()

# Delete audiocut
shutil.rmtree(path)

# Write to output file
f = open('transcribe_output.txt', 'w', encoding='utf-8')
f.write(string)
f.close()
