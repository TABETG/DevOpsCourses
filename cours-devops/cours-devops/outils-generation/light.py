import re, glob, pathlib
for f in sorted(glob.glob('/mnt/user-data/outputs/devops-*.html')):
    s = pathlib.Path(f).read_text()
    s = re.sub(r'@media \(prefers-color-scheme: dark\)\{ :root:not\(\[data-theme="light"\]\)\{.*?\}\}\n', '', s, count=1, flags=re.S)
    s = s.replace("var dark=cur?cur==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;", "var dark=cur==='dark';")
    pathlib.Path(f).write_text(s)
    print(f.split('/')[-1], 'prefers-color-scheme' in s, "cur==='dark';" in s)
