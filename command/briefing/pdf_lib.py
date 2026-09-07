#!/usr/bin/env python3
"""Deep emotional bilingual natal readings (M + Mai) — human-voiced, long-form.

Follows astrology-reading-prose skill: image-first TH prose, EN rewritten not
translated, wound->gift arc every section, numbers as witnesses only.
Layout: one theme per page pair-section, generous whitespace, no overlap.
"""
import os, random, math
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph, Frame, Spacer

pdfmetrics.registerFont(TTFont('Thai', 'C:/Windows/Fonts/tahoma.ttf'))
pdfmetrics.registerFont(TTFont('ThaiB', 'C:/Windows/Fonts/tahomabd.ttf'))
pdfmetrics.registerFont(TTFont('Georgia', 'C:/Windows/Fonts/georgia.ttf'))
pdfmetrics.registerFont(TTFont('GeorgiaI', 'C:/Windows/Fonts/georgiai.ttf'))
pdfmetrics.registerFont(TTFont('GeorgiaB', 'C:/Windows/Fonts/georgiab.ttf'))
pdfmetrics.registerFont(TTFont('PalatinoI', 'C:/Windows/Fonts/palai.ttf'))

W, H = A4
NAVY = HexColor('#0a0e26'); GOLD = HexColor('#e6c35c'); GOLD_D = HexColor('#9c7c2c')
CREAM = HexColor('#f5eeda'); LILAC = HexColor('#c3b0f0'); MUTED = HexColor('#8f96bd')

S_TH_H = ParagraphStyle('thh', fontName='ThaiB', fontSize=13.5, leading=20, textColor=GOLD, spaceAfter=5)
S_TH   = ParagraphStyle('th',  fontName='Thai', fontSize=10.8, leading=19.5, textColor=CREAM, spaceAfter=7)
S_EN_H = ParagraphStyle('enh', fontName='GeorgiaB', fontSize=12, leading=16, textColor=LILAC, spaceAfter=3)
S_EN   = ParagraphStyle('en',  fontName='Georgia', fontSize=10, leading=16, textColor=CREAM, spaceAfter=6)
S_I    = ParagraphStyle('i', fontName='PalatinoI', fontSize=12.5, leading=19, textColor=LILAC, alignment=TA_CENTER, spaceAfter=8)

def bg(cv, page_no):
    cv.setFillColor(NAVY); cv.rect(0, 0, W, H, stroke=0, fill=1)
    random.seed(100 + page_no)
    for _ in range(4):
        x, y = random.uniform(0,W), random.uniform(0,H)
        for r, col in [(52*mm, Color(.09,.10,.30,.55)), (34*mm, Color(.14,.09,.28,.45))]:
            cv.setFillColor(col); cv.circle(x, y, r, stroke=0, fill=1)
    for _ in range(110):
        x, y = random.uniform(4*mm, W-4*mm), random.uniform(4*mm, H-4*mm)
        s = random.choice([.5,.7,.9,1.1])
        cv.setFillColor(HexColor(random.choice(['#ffffff','#ffe9b0','#cfd6ff','#ffd9ec'])))
        cv.circle(x, y, s, stroke=0, fill=1)
        if random.random() < .08:
            cv.setStrokeColor(HexColor('#ffffff')); cv.setLineWidth(.4)
            cv.line(x-2.4,y,x+2.4,y); cv.line(x,y-2.4,x,y+2.4)
    cv.setStrokeColor(GOLD_D); cv.setLineWidth(.9)
    for (cx, cy, a0) in [(0,H,0),(W,H,90),(W,0,180),(0,0,270)]:
        p = cv.beginPath(); p.arc(cx-16*mm, cy-16*mm, cx+16*mm, cy+16*mm, a0+18, 54)
        cv.drawPath(p, stroke=1, fill=0)
        p2 = cv.beginPath(); p2.arc(cx-11*mm, cy-11*mm, cx+11*mm, cy+11*mm, a0+24, 42)
        cv.setLineWidth(.6); cv.drawPath(p2, stroke=1, fill=0)


def moon_phase(cv, cx, cy, r):
    cv.setFillColor(CREAM); cv.circle(cx, cy, r, stroke=0, fill=1)
    cv.setFillColor(NAVY);  cv.circle(cx+r*.72, cy+r*.25, r*.92, stroke=0, fill=1)
    cv.setFillColor(GOLD);  cv.circle(cx-r*.15, cy-r*.1, r*.16, stroke=0, fill=1)

def divider(cv, y, half=46*mm):
    cx = W/2
    cv.setStrokeColor(GOLD); cv.setLineWidth(.7)
    cv.line(cx-half, y, cx-8*mm, y); cv.line(cx+8*mm, y, cx+half, y)
    cv.setFillColor(GOLD)
    p = cv.beginPath(); p.moveTo(cx, y+2.2*mm); p.lineTo(cx+2.2*mm, y); p.lineTo(cx, y-2.2*mm); p.lineTo(cx-2.2*mm, y); p.close()
    cv.drawPath(p, stroke=0, fill=1)
    cv.circle(cx-8*mm, y, .9*mm, stroke=0, fill=1); cv.circle(cx+8*mm, y, .9*mm, stroke=0, fill=1)

def zodiac_ring(cv, cx, cy, r):
    cv.setStrokeColor(GOLD_D); cv.setLineWidth(.8)
    cv.circle(cx, cy, r, stroke=1, fill=0); cv.circle(cx, cy, r*.78, stroke=1, fill=0)
    for i in range(12):
        a = math.radians(i*30)
        cv.line(cx+r*.78*math.cos(a), cy+r*.78*math.sin(a), cx+r*math.cos(a), cy+r*math.sin(a))
        tx, ty = cx+(r+2.2)*math.cos(a), cy+(r+2.2)*math.sin(a)
        cv.setFillColor(GOLD if i%3 else CREAM); cv.circle(tx, ty, .55, stroke=0, fill=1)
    cv.setFillColor(GOLD)
    p = cv.beginPath(); p.moveTo(cx, cy+2.4); p.lineTo(cx+2.4, cy); p.lineTo(cx, cy-2.4); p.lineTo(cx-2.4, cy); p.close()
    cv.drawPath(p, stroke=0, fill=1)

def footer(cv, n):
    moon_phase(cv, W/2, 13.5*mm, 2.6*mm)
    cv.setFillColor(MUTED); cv.setFont('PalatinoI', 9)
    cv.drawString(W/2+6*mm, 12.2*mm, 'Universe Engine · Astral Astrology')
    cv.drawRightString(W-14*mm, 12.2*mm, f'— {n} —')

def header(cv, title, sub):
    zodiac_ring(cv, 20*mm, H-22*mm, 9*mm)
    cv.setFillColor(GOLD); cv.setFont('ThaiB', 17)
    cv.drawCentredString(W/2, H-24*mm, title)
    cv.setFillColor(MUTED); cv.setFont('PalatinoI', 10)
    cv.drawCentredString(W/2, H-29.5*mm, sub)
    divider(cv, H-33.5*mm)

def card_badge(cv, x, y, label):
    cv.setStrokeColor(GOLD); cv.setFillColor(HexColor('#141a44')); cv.setLineWidth(1.2)
    cv.circle(x, y, 6.2*mm, stroke=1, fill=1)
    cv.setStrokeColor(GOLD_D); cv.setLineWidth(.5); cv.circle(x, y, 5.2*mm, stroke=1, fill=0)
    cv.setFillColor(GOLD); cv.setFont('GeorgiaB', 11); cv.drawCentredString(x, y-1.6*mm, label)

def frame(y_bot, y_top):
    return Frame(20*mm, y_bot, W-40*mm, y_top-y_bot, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

def render_pages(c, fname, person_th, person_en, birth_line, pages):
    """pages: list of (header_title, header_sub, [blocks]); block = dict(no, th_h, th, en_h, en)."""
    c.setTitle(f'Deep Natal Reading — {person_en} · Universe Engine')
    page = 0
    for ptitle, psub, blocks in pages:
        page += 1
        bg(c, page)
        if page == 1:
            zodiac_ring(c, W/2, H-54*mm, 15*mm)
            moon_phase(c, W/2, H-54*mm, 5.5*mm)
            c.setFillColor(GOLD); c.setFont('GeorgiaB', 23)
            c.drawCentredString(W/2, H-86*mm, ptitle)
            c.setFillColor(CREAM); c.setFont('ThaiB', 13)
            c.drawCentredString(W/2, H-94*mm, person_th)
            divider(c, H-101*mm, half=56*mm)
            c.setFillColor(MUTED); c.setFont('PalatinoI', 10.5)
            c.drawCentredString(W/2, H-107*mm, birth_line)
            f = frame(112*mm, 28*mm)
            story = []
            for b in blocks[:2]:
                story.append(Spacer(1,2))
                story.append(Paragraph(b['th_h'], S_TH_H))
                story.append(Paragraph(b['th'], S_TH))
                story.append(Paragraph(b['en_h'], S_EN_H))
                story.append(Paragraph(b['en'], S_EN))
                story.append(Spacer(1,3))
            f.addFromList(story, c)
        elif len(blocks) == 1:
            header(c, ptitle, psub)
            card_badge(c, 24*mm, H-42*mm, blocks[0]['no'])
            fb = frame(48*mm, 30*mm)
            fb.addFromList([
                Paragraph(blocks[0]['th_h'], S_TH_H),
                Paragraph(blocks[0]['th'], S_TH),
                Paragraph(blocks[0]['en_h'], S_EN_H),
                Paragraph(blocks[0]['en'], S_EN),
            ], c)
        else:
            header(c, ptitle, psub)
            half = (H - 46 - 30) / 2
            ys = [(H-46*mm, H-46*mm-half), (H-46*mm-half-4, 30)]
            # use mm consistently: compute in mm then convert handled by Frame args in mm units already
            for bi, (ytop_mm, ybot_mm) in enumerate(ys):
                if bi >= len(blocks): break
                b = blocks[bi]
                card_badge(c, 24*mm, ytop_mm + 4, str(b['no']))
                fb = Frame(20*mm, ybot_mm, W-40*mm, ytop_mm - ybot_mm,
                           leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
                fb.addFromList([
                    Paragraph(b['th_h'], S_TH_H),
                    Paragraph(b['th'], S_TH),
                    Paragraph(b['en_h'], S_EN_H),
                    Paragraph(b['en'], S_EN),
                ], c)
        footer(c, page); c.showPage()
    c.save()
    print('saved:', fname, os.path.getsize(fname))
