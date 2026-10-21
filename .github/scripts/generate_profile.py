"""Generate self-hosted SVG artwork from public GitHub data; standard library only."""
import argparse
import html
import json
import math
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets'
USER = 'garvpahwa007'
MINT, CYAN, PURPLE, WHITE, MUTED = '#52f5bf', '#55cfff', '#a78bfa', '#edf6ff', '#8fa7b9'


def api(path, payload=None):
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('Set GITHUB_TOKEN to read the GitHub GraphQL API.')
    req = urllib.request.Request('https://api.github.com/' + path,
        data=json.dumps(payload).encode() if payload else None,
        headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                 'User-Agent': 'garvpahwa007-profile', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=45) as response:
        result = json.load(response)
    if isinstance(result, dict) and result.get('errors'):
        raise RuntimeError(result['errors'])
    return result


def fetch():
    query = '''query($login:String!) { user(login:$login) {
      followers { totalCount }
      contributionsCollection { contributionCalendar {
        totalContributions weeks { contributionDays { date contributionCount } }
      } }
    } }'''
    user = api('graphql', {'query': query, 'variables': {'login': USER}})['data']['user']
    repos, page = [], 1
    while True:
        batch = api(f'users/{USER}/repos?type=owner&per_page=100&page={page}')
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    languages = {}
    for repo in repos:
        if repo['fork'] or repo['name'].lower() == USER.lower():
            continue
        for name, size in api(f"repos/{USER}/{repo['name']}/languages").items():
            languages[name] = languages.get(name, 0) + size
    return {'user': user, 'repos': repos, 'languages': languages}


def text(x, y, value, size=14, color=WHITE, weight=400, mono=False, extra=''):
    family = "'SFMono-Regular',Consolas,monospace" if mono else "-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif"
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" font-weight="{weight}" {extra}>{html.escape(str(value))}</text>'


def rect(x, y, w, h, fill, stroke='none', r=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'


def svg(w, h, title, body, description=''):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(description or title)}</desc>
<defs>
 <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0b1925"/><stop offset="1" stop-color="#060e17"/></linearGradient>
 <radialGradient id="aura"><stop stop-color="#163c48" stop-opacity=".7"/><stop offset="1" stop-color="#07111b" stop-opacity="0"/></radialGradient>
</defs>
{rect(1, 1, w-2, h-2, 'url(#bg)', '#203744', 18)}
{body}
</svg>'''


def chip(x, y, label, color=MINT):
    width = len(label) * 7 + 25
    return rect(x, y, width, 28, '#0c202b', '#24414d', 7) + text(x+12, y+19, label, 12, color, 500, True), width


def hero(data):
    u, repos = data['user'], data['repos']
    b = '<path d="M560 1V268M600 1V268M640 1V268M680 1V268M720 1V268M760 1V268M800 1V268M840 1V268M880 1V268M920 1V268M560 28H959M560 68H959M560 108H959M560 148H959M560 188H959M560 228H959" stroke="#183340" opacity=".32"/>'
    b += '<ellipse cx="758" cy="132" rx="205" ry="155" fill="url(#aura)"/>'
    b += '<circle cx="37" cy="36" r="4" fill="#52f5bf"><animate attributeName="opacity" values="1;.3;1" dur="3s" repeatCount="indefinite"/></circle>'
    b += text(50, 41, "@garvpahwa007  /  BUILDER'S LOG", 12, MINT, 500, True)
    b += text(32, 112, 'Garv Pahwa', 58, WHITE, 700)
    b += text(35, 149, 'Code. Build. Take flight.', 23, CYAN, 500)
    b += text(35, 182, 'Computer science student exploring robotics,', 16, MUTED)
    b += text(35, 206, 'drones, and the systems that make things move.', 16, MUTED)
    x = 35
    for label, color in [('C / C++', CYAN), ('ROBOTICS', MINT), ('DRONES', PURPLE), ('CAD', CYAN)]:
        shape, width = chip(x, 224, label, color)
        b += shape
        x += width + 8
    b += '<g fill="none" stroke="#22535c"><ellipse cx="762" cy="141" rx="148" ry="81" stroke-dasharray="3 8"/><ellipse cx="762" cy="141" rx="123" ry="64"/><path d="M598 141h34m260 0h34M762 47v20m0 149v20"/></g>'
    b += '<g fill="none" stroke="#52f5bf" stroke-width="3" stroke-linejoin="round"><path d="M735 123L679 93m108 30l56-30m-108 64l-56 30m108-30l56 30" stroke-width="12" stroke="#183d49"/><path d="M735 123L679 93m108 30l56-30m-108 64l-56 30m108-30l56 30"/>'
    for x, y in [(676, 91), (846, 91), (676, 189), (846, 189)]:
        b += f'<ellipse cx="{x}" cy="{y}" rx="43" ry="16" fill="#0b2631" stroke="#31726f"/><ellipse cx="{x}" cy="{y}" rx="33" ry="9" stroke="#52f5bf" stroke-dasharray="40 12"><animate attributeName="stroke-dashoffset" from="0" to="104" dur="2s" repeatCount="indefinite"/></ellipse><circle cx="{x}" cy="{y}" r="4" fill="#55cfff" stroke="none"/>'
    b += '<path d="M738 114h46l15 28-15 27h-46l-15-27z" fill="#102d3a"/><path d="M748 126h27l9 16-9 15h-27l-9-15z" fill="#133f48" stroke="#55cfff"/><circle cx="762" cy="142" r="5" fill="#52f5bf" stroke="none"/></g>'
    b += text(698, 246, 'IDEAS → PROTOTYPES', 11, MUTED, 400, True)
    b += '<path d="M1 270H959" stroke="#203744"/>'
    values = [(len(repos), 'PUBLIC REPOS', CYAN), (sum(r['stargazers_count'] for r in repos), 'REPO STARS', PURPLE), (u['contributionsCollection']['contributionCalendar']['totalContributions'], 'CONTRIBUTIONS / YEAR', MINT), (u['followers']['totalCount'], 'FOLLOWERS', CYAN)]
    for i, (value, label, color) in enumerate(values):
        x = 34 + i * 238
        if i:
            b += f'<path d="M{x-18} 288V329" stroke="#203744"/>'
        b += text(x, 315, f'{value:,}', 30, color, 650)
        b += text(x, 337, label, 10, MUTED, 500, True)
    return svg(960, 356, 'Garv Pahwa — Code. Build. Take flight.', b,
               '; '.join(f'{value} {label.lower()}' for value, label, _ in values))


def city(data):
    calendar = data['user']['contributionsCollection']['contributionCalendar']
    weeks = calendar['weeks'][-26:]
    days = [d for w in weeks for d in w['contributionDays']]
    total = sum(d['contributionCount'] for d in days)
    active = sum(d['contributionCount'] > 0 for d in days)
    peak = max((d['contributionCount'] for d in days), default=0)
    b = text(32, 43, "The city I'm building", 27, WHITE, 650)
    b += text(32, 70, 'Every block starts with showing up.', 14, MUTED)
    b += text(926, 43, '02 / CONTRIBUTION CITY', 10, MINT, 400, True, 'text-anchor="end"')
    b += text(34, 125, 'LAST 26 WEEKS', 11, MINT, 500, True)
    b += text(30, 180, f'{total:,}', 57, WHITE, 650)
    b += text(34, 206, 'contributions', 14, MUTED)
    b += text(34, 245, f'{active} active days', 13, MUTED, 400, True)
    b += text(34, 269, f'Busiest day: {peak}', 12, MUTED, 400, True)
    b += '<ellipse cx="578" cy="256" rx="325" ry="125" fill="url(#aura)"/>'
    blocks = []
    for w, week in enumerate(weeks):
        for d, day in enumerate(week['contributionDays']):
            x, y = 238 + (w + d) * 19, 306 + (d - w) * 5.2
            count = day['contributionCount']
            height = 0 if not count else 7 + math.sqrt(count / max(peak, 1)) * 99
            blocks.append((y, x, height, count, day['date']))
    for y, x, height, count, date in sorted(blocks):
        b += f'<g><title>{date}: {count} contributions</title>'
        if height:
            b += f'<path d="M{x-18},{y-6.4-height}L{x},{y-height}V{y}L{x-18},{y-6.4}Z" fill="#108471" stroke="#155449" stroke-width=".7"/>'
            b += f'<path d="M{x},{y-height}L{x+18},{y-6.4-height}V{y-6.4}L{x},{y}Z" fill="#16b69b" stroke="#155449" stroke-width=".7"/>'
            for level in range(22, int(height), 22):
                b += f'<path d="M{x-18},{y-6.4-level}L{x},{y-level}L{x+18},{y-6.4-level}" fill="none" stroke="#62efcc" opacity=".35" stroke-width=".65"/>'
        fill, stroke = (MINT, '#b1ffe6') if count else ('#0c2b32', '#17444b')
        b += f'<path d="M{x},{y-12.8-height}L{x+18},{y-6.4-height}L{x},{y-height}L{x-18},{y-6.4-height}Z" fill="{fill}" stroke="{stroke}" stroke-width=".75"/></g>'
    b += '<path d="M32 363H928" stroke="#203744"/>'
    b += text(34, 390, '26 weeks · blocks represent daily activity', 11, MUTED, 400, True)
    b += text(925, 390, f"{days[0]['date']} → {days[-1]['date']}", 10, MINT, 400, True, 'text-anchor="end"')
    return svg(960, 412, "Garv's contribution city", b,
               f'{total} contributions across {active} active days in the last 26 weeks. Busiest day: {peak}. Each building represents real daily GitHub activity.')


def languages(data):
    values = sorted(data['languages'].items(), key=lambda x: x[1], reverse=True)
    total = sum(v for _, v in values)
    b = text(32, 40, 'Language stack', 23, WHITE, 650)
    b += text(32, 65, 'Public source bytes · profile repo excluded', 12, MUTED)
    b += text(925, 40, '03 / STACK.SCAN', 10, MINT, 400, True, 'text-anchor="end"')
    colors = {'C': CYAN, 'C++': PURPLE, 'Python': '#f3ce62', 'Makefile': MINT, 'TypeScript': '#6ea5ff', 'JavaScript': '#f3ce62'}
    if not total:
        b += text(32, 110, 'No language data available yet.', 14, MUTED)
    for i, (name, size) in enumerate(values[:4]):
        y, percent = 100 + i * 34, size / total * 100
        color = colors.get(name, PURPLE)
        b += f'<circle cx="38" cy="{y-4}" r="5" fill="{color}"/>'
        b += text(53, y, name, 14, WHITE, 500)
        b += text(481, y, f'{percent:.1f}%', 12, color, 500, True, 'text-anchor="end"')
        b += rect(184, y-13, 220, 11, '#102c38', r=5)
        b += rect(184, y-13, max(2, 220*percent/100), 11, color, r=5)
    b += '<path d="M524 87V166" stroke="#203744"/>'
    b += text(555, 102, 'BEYOND THE CODE', 10, MINT, 500, True)
    b += text(555, 130, 'Robotics · drones · autonomous systems', 15, WHITE, 500)
    b += text(555, 155, 'CAD, mechanical design & hands-on experiments', 12, MUTED)
    height = max(194, 113 + min(len(values), 4) * 34)
    if len(values) > 4:
        b += text(32, height-13, 'Top 4 languages shown; percentages use all public source bytes.', 10, MUTED)
    return svg(960, height, 'Public repository language breakdown', b,
               ', '.join(f'{name}: {size/total*100:.1f}%' for name, size in values) if total else 'No public source language data yet.')


PROJECTS = [
    ('c-programs', 'C-Programs', 'Terminal games, calculators, and the', 'fundamentals behind working programs.', 'C', CYAN, '01'),
    ('selected-programs', 'Selected-programs', 'A curated collection of C programs:', 'banking, games, and everyday logic.', 'C / PRACTICE', MINT, '02'),
    ('autocad', 'AutoCAD', 'A mecanum wheel model and engineering', 'references for things that move.', 'CAD / HARDWARE', PURPLE, '03'),
    ('progress-meter', 'Progress-Meter', 'A collaborative progress-tracking project', 'built for SIH 2026.', 'COLLABORATION', CYAN, '04'),
]


def project_card(project):
    slug, name, line1, line2, tag, color, number = project
    b = text(22, 30, f'PROJECT / {number}', 10, color, 500, True)
    b += text(442, 32, '↗', 23, color, 500, extra='text-anchor="end"')
    b += text(22, 64, name, 24, WHITE, 650)
    b += text(22, 93, line1, 13, MUTED)
    b += text(22, 113, line2, 13, MUTED)
    shape, _ = chip(22, 134, tag, color)
    b += shape
    b += text(441, 154, 'VIEW REPOSITORY', 9, MUTED, 400, True, 'text-anchor="end"')
    return svg(470, 180, name, b, f'{line1} {line2}')


def render(data):
    OUT.mkdir(exist_ok=True)
    files = {'header.svg': hero(data), 'contribution-city.svg': city(data), 'languages.svg': languages(data)}
    files.update({f'project-{p[0]}.svg': project_card(p) for p in PROJECTS})
    for name, value in files.items():
        (OUT / name).write_text(value + '\n', encoding='utf-8')
    print(f'Generated {len(files)} profile assets from GitHub data.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, help='Render from a local JSON snapshot without network access')
    args = parser.parse_args()
    data = json.loads(args.snapshot.read_text()) if args.snapshot else fetch()
    render(data)
