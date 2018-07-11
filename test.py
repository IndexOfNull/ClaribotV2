from PIL import ImageFont, Image, ImageDraw

def text_wrap(text,**kwargs): #Wrap text, break by word or letter
    font = kwargs.pop('font')
    count_width = kwargs.pop('width',None)
    max_pixels = kwargs.pop('max_pixels',None)
    br = kwargs.pop('wrap',None)
    if not count_width and not max_pixels:
        return text
    lines = []
    cur_len = 0
    cur_text = ''
    for i,char in enumerate(text):
        if char == "\n":
            print(cur_text)
            lines.append(cur_text)
            cur_len = 0
            cur_text = ''
            continue
        cur_text += char
        cur_len = font.getsize(cur_text)[0]
        next_len = font.getsize(cur_text + text[i])[0]
        print(cur_text,cur_len,next_len)
        if next_len > max_pixels:
            if br == 'letter' or br is None:
                lines.append(cur_text)
                cur_len = 0
                cur_text = ''
            elif br == 'word':
                lastword = cur_text.split(' ')
                if len(lastword) == 1:
                    lines.append(cur_text)
                    cur_len = 0
                    cur_text = ''
                else:
                    lines.append(' '.join(lastword[:-1]))
                    cur_text = lastword[-1:][0]
                    print(cur_text)
                    cur_len = font.getsize(cur_text)[0]
    lines.append(cur_text)
    return lines

font = ImageFont.truetype("resource/font/GenBasR.ttf",28)
print(text_wrap('The automan empire was the absolute best empire i dont think i have good spelling.',font=font,max_pixels=285,wrap='word'))
