"""Identify one ordinary Android immersive-mode education notice, never permissions."""
import re
import xml.etree.ElementTree as ET


def known_guide_button(xml):
    try:nodes=list(ET.fromstring(xml).iter('node'))
    except ET.ParseError:raise ValueError('UI hierarchy invalid') from None
    allowed={'android','com.android.systemui'}
    if not any(n.get('package') in allowed and n.get('text')=='Viewing full screen' for n in nodes):
        raise ValueError('Known non-binding fullscreen notice not observed')
    candidates=[n for n in nodes if n.get('package') in allowed and n.get('text')=='Got it' and n.get('enabled','true')=='true']
    if len(candidates)!=1:raise ValueError('Fullscreen notice acknowledgement is ambiguous')
    match=re.fullmatch(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',candidates[0].get('bounds',''))
    if not match:raise ValueError('Fullscreen button geometry missing')
    x1,y1,x2,y2=map(int,match.groups())
    if not (0<=x1<x2<=10000 and 0<=y1<y2<=10000):raise ValueError('Fullscreen button geometry invalid')
    return ((x1+x2)//2,(y1+y2)//2)
