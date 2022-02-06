import os
from urllib import parse

fns_ignore = {'.git','.gitignore'}
sufs_ignore = {
    'py','md',
    'avi','mp4','flv',
    }
prev_count = 6

def is_img_file(fn:str):
    suf = fn.rsplit('.',1)[-1]
    return suf not in sufs_ignore

def url_join(s1,s2):
    if not s1:return s2
    return f'{s1}/{s2}'

def sample_dir(path:str,root=''):
    its = []
    for fn in os.listdir(path):
        if fn in fns_ignore:continue
        rfn = os.path.join(path,fn)
        pfn = url_join(root,fn)
        if os.path.isfile(rfn):
            if is_img_file(fn):
                yield pfn
            continue
        it = sample_dir(rfn,pfn)
        yield next(it)
        its.append(it)
    while its:
        t = []
        for it in its:
            try:
                yield next(it)
            except StopIteration:
                continue
            t.append(it)
        its = t

def preview_dir(path:str):
    imgs = []
    subprev = []
    for fn in os.listdir(path):
        if fn in fns_ignore:continue
        rfn = os.path.join(path,fn)
        if os.path.isfile(rfn):
            if is_img_file(fn):
                imgs.append(fn)
            continue
        prevs = []
        for _,t in zip(range(prev_count),sample_dir(rfn,fn)):
            prevs.append(t)
        subprev.append((fn,prevs))
    return imgs,subprev

def format_img(pfn:str):
    t = parse.quote(pfn)
    img = f'[<img src="{t}">]({pfn})'
    return img

def format_prev(name:str,imgs:list):
    a = f'[{name}]({name})'
    imgs = [format_img(img) for img in imgs]
    imgs = ''.join(imgs)
    if imgs:
        a += '\n\n' + imgs
    return a

def format_dir(imgs:list,subprev:list):
    t = []
    for name,prev in subprev:
        t.append(format_prev(name,prev))
    imgs = [format_img(img) for img in imgs]
    imgs = ''.join(imgs)
    if imgs:
        t.append(imgs)
    t = '\n\n---\n\n'.join(t)
    return t

def main_dir(path:str):
    imgs,subprev = preview_dir(path)
    md = format_dir(imgs,subprev)
    if path == '.':
        with open('README_root.md','r',encoding='utf-8') as f:
            s = f.read()
        md = s.strip() + '\n\n---\n\n' + md
    else:
        name = os.path.split(path)[-1]
        md = f'# {name}\n\n{md}'
    fn = os.path.join(path,'README.md')
    with open(fn,'w',encoding='utf-8') as f:
        f.write(md)
    for fn in os.listdir(path):
        if fn in fns_ignore:continue
        rfn = os.path.join(path,fn)
        if os.path.isdir(rfn):
            main_dir(rfn)

if __name__ == '__main__':
    main_dir('.')
