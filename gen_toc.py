import os
from urllib import parse
import matplotlib.pyplot as plt

fns_ignore = {'.git','.gitignore'}
sufs_ignore = {
    'py','md',
    'avi','mp4','flv','wmv','mpg','svg',
    }
prev_count = 6
img_max_width = 120
img_max_height = 150

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
                yield rfn,pfn
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
                imgs.append((rfn,fn))
            continue
        prevs = []
        for _,t in zip(range(prev_count),sample_dir(rfn,fn)):
            prevs.append(t)
        subprev.append((fn,prevs))
    return imgs,subprev

def format_img(rfn:str,pfn:str):
    args = ['img']
    ufn = parse.quote(pfn)
    args.append(f'src="{ufn}"')
    name = pfn.rsplit('/',1)[-1]
    name = name.rsplit('.',1)[0]
    args.append(f'alt="{name}"')
    t = plt.imread(rfn)
    if t is None:
        print(rfn)
    h,w,*_ = t.shape
    pw = w / img_max_width
    ph = h / img_max_height
    if pw > 1 or ph > 1:
        if pw > ph:
            args.append(f'width={img_max_width}px')
        else:
            args.append(f'height={img_max_height}px')
    args = ' '.join(args)
    img = f'[<{args}>]({ufn})'
    return img

def format_prev(name:str,imgs:list):
    a = f'[{name}]({name})'
    imgs = [format_img(*t) for t in imgs]
    imgs = ''.join(imgs)
    if imgs:
        a += '\n\n' + imgs
    return a

def format_dir(imgs:list,subprev:list):
    t = []
    for name,prev in subprev:
        t.append(format_prev(name,prev))
    imgs = [format_img(*t) for t in imgs]
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
