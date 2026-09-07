#!/usr/bin/env python3
"""Build the two human-voiced bilingual reading PDFs (M + Mai) using pdf_lib."""
import os
from pdf_lib import render_pages

OUT_M = os.path.expanduser('~/Desktop/Natal_Reading_M_TH_EN.pdf')
OUT_MA = os.path.expanduser('~/Desktop/Natal_Reading_Mai_TH_EN.pdf')

# ==================== M — หน้า 1 (ปก+แก่น) =================
m1 = ('DEEP NATAL READING', None, [
 dict(no='1',
  th_h='เตาหลอมที่ทนไฟ',
  th='มีคนบอกคุณไหมว่าคุณนิ่งผิดปกติ ความจริงคือคุณไม่ได้นิ่งเพราะไม่รู้สึกอะไร คุณนิ่งเพราะคุณรับได้มากกว่าคนอื่น ดวงอาทิตย์กับลัคนาของคุณอยู่ราศีเดียวกันทั้งคู่ พฤษภ ตั้งแต่เกิด ภายนอกที่โลกเห็นกับแก่นข้างในเป็นดินก้อนเดียวกัน คนรอบข้างพังไปแล้วตรงที่คุณยังยืนอยู่',
  en_h='A furnace that holds fire',
  en='People may call you unusually calm. The truth is you are not calm because you feel nothing; you are calm because you can hold more than most. Your Sun and Ascendant share one sign, Taurus, since the day you were born. The outside world and your inner core are made of the same earth.'),
 dict(no='2',
  th_h='ดาวฤกษ์หลวง — เสน่ห์ที่มาพร้อมเกียรติ',
  th='ศุกร์ของคุณคือดาวที่แข็งแกร่งที่สุดในดวง เจ้าเรือนลัคนาที่คอยดูแลทุกการตัดสินใจ และมันจับมือกับดาวฤกษ์หลวงอัลดิบารันห่างเพียงเสี้ยวองศา แปลว่าความสวยงาม รสนิยม และเสน่ห์ของคุณ มาพร้อมเงื่อนไขเดียวคือ ซื่อสัตย์กับมัน ความสำเร็จของคุณไม่ใช่ของที่ปล้ำมา มันคือของที่คุณสร้างทีละชิ้นจนคนเริ่มหันมามองเอง',
  en_h='The royal star — Venus with Aldebaran',
  en='Your Venus is the strongest planet in this chart: chart ruler, guardian of every decision. And it stands 0.41 degrees from Aldebaran, a royal star of Persia. Charm, taste and financial gifts all come with one condition attached: honesty. Your success is not seized. It is built piece by piece until people turn to look on their own.'),
])
# ==================== M — หน้า 2 (วงจรปี) =================
m2 = ('วงจรปี · ตถุดาว · ดาวเคราะห์น้อย', 'Varshaphal · Zi Wei · Asteroids', [
 dict(no='3',
  th_h='วรรษผล — สองปีของการสะสมความสัมพันธ์',
  th='ปี 2026 มุณฐะของคุณยืนอยู่ในตุลย์ และดาวพฤหัสฯ เป็นเจ้าปี ดาวแห่งการขยาย ปีนี้ของขวัญมาทาง "คน" ไม่ใช่ทางเงินหรือโชค คนที่คุณเคยช่วยไว้จะกลับมาเปิดประตู · ปี 2027 มุณฐะย้ายเข้าพิจิก ยังคงเจ้าปีพฤหัสฯ ความลึกทางอารมณ์ที่คุณฝังไว้จะกลายเป็นทรัพยากรจริง สองปีนี้ไม่ใช่ปีของการวิ่งแข่ง มันคือปีของการปลูกต้นไม้ที่จะให้ร่มเงาอีกสิบปี',
  en_h='Varshaphal — two years of building relational capital',
  en='In 2026 your Muntha stands in Libra with Jupiter as year lord, the great expander. This year gifts arrive through people, not luck or money: doors opened by those you once helped. In 2027 Muntha slips into Scorpio, Jupiter still lord. The emotional depth you buried becomes real currency. These two years are not for racing. They are for planting trees that will shade the next decade.'),
 dict(no='4',
  th_h='ตถุดาว — วังชีวิตแห่งปีเสือ',
  th='คุณเกิดเดือนจันทรคติสี่ วันที่สิบสาม ชั่วโมง卯 วังชีวิตของคุณจึงอยู่ที่ 寅 ปีเสือ บทบาทชีวิตของคุณตามผังนี้คือผู้เริ่มต้นที่นำพาคนอื่นออกจากป่า ไม่ใช่คนที่รอใครมาชี้ทาง ส่วนดาวประจำปี 2026 ขัดที่ 子 และ 2027 ที่ 丑 ช่วงนี้เอกสารสำคัญและคำสัญญาต้องอ่านสองรอบก่อนเซ็น',
  en_h='Zi Wei Dou Shu — Life Palace in the Tiger year',
  en='Born in lunar month four, day thirteen, at the Mao hour, your Life Palace sits in Yin, the Tiger. This chart casts you as the initiator who walks others out of the forest, not the one waiting to be led. The annual star clashes at Zi in 2026 and Chou in 2027: read important documents twice before signing.'),
 dict(no='5',
  th_h='ไครอน — แผลเรื่องความยุติธรรมที่กลายเป็นของขวัญ',
  th='ไครอนของคุณอยู่ตาชั่ง 26 องศา ถอยหลัง บาดแผลที่ลึกที่สุดของคุณเกี่ยวกับความไม่ยุติธรรม คุณเคยเจอเรื่องที่ควรเป็นแบบนั้นแต่กลับเป็นแบบนี้ มาพอ ๆ กันจนเบื่อคำว่ายุติธรรม แต่ฟังให้ดี: คนที่เคยถูกปฏิเสธความยุติธรรม มักกลายเป็นคนเดียวในห้องที่มองเห็นเมื่อใครบางคนกำลังถูกเหยียบ นี่คือของขวัญที่ซ่อนอยู่ในบาดแผลของคุณ คุณกลายเป็นคนช่วยคนอื่นหาสมดุล เพราะคุณรู้ว่าความไม่สมดุลรู้สึกยังไง',
  en_h='Chiron — the wound about fairness that became a gift',
  en='Your Chiron sits at 26 Libra retrograde. The deepest wound is about injustice: you watched things that should have gone one way go another, enough times to grow tired of the word fair. But listen closely. Those who were once denied justice often become the only person in the room who sees when someone else is being crushed. That is the gift hidden in your wound. You became a restorer of balance because you know exactly what imbalance feels like from inside.'),
])
# ==================== M — หน้า 3 (เลข/หยี่/ดาวเก้า/mayan) =================
m3 = ('เลขศาสตร์ · หยี่จิ๋ง · ดาวเก้าเก่า · ทซอลกิน', 'Numerology · I Ching · Nine Star Ki · Dreamspell', [
 dict(no='6',
  th_h='เลขศาสตร์ — เส้นทางแห่งเสรีภาพ',
  th='Life Path ของคุณคือ 5 ชีวิตของคุณเรียนรู้ผ่านผิวหนัง ไม่ใช่ผ่านหน้ากระดาษ เสรีภาพสำหรับคุณคือออกซิเจน และสิ่งเดียวที่ทำให้คุณหมดพลังคือการถูกมัดให้อยู่ที่เดิม ปี 2026 เป็น Personal Year 7 ปีที่จักรวาลขอให้คุณเงียบ อ่าน ไตร่ตรอง อย่าฝืนวิ่ง · แล้ว 2027 คือปีที่ 8 ปีเก็บเกี่ยว การเงินและอำนาจจะมาหาสิ่งที่คุณเงียบไว้ทั้งปี',
  en_h='Numerology — the freedom path',
  en='Your Life Path is 5. You learn through skin, not paper. Freedom is oxygen, and the only thing that truly drains you is being tied to one place. 2026 runs as a Personal Year 7: the universe asks for quiet, reading, reflection. Do not force the sprint. Then 2027 arrives as an 8 year: harvest. Money and authority find whatever you spent this year becoming quietly.'),
 dict(no='7',
  th_h='หยี่จิ๋ง — 泰 ประชา ความร่มเย็น',
  th='เส้นของคุณหกเส้นจัดเรียงเป็นสวรรค์อยู่ใต้ พื้นพิภพอยู่เหนือ ได้คำตอบเป็นสำเนาคำทำนายที่สงบที่สุดในคัมภีร์ทั้งเล่ม ประชา แปลว่าเล็กออกไป ใหญ่เข้ามา ความเจริญของคุณไม่ใช่การเอาชนะใคร แต่คือการจัดวางให้สิ่งเล็กและสิ่งใหญ่ต่างคนต่างอยู่ถูกที่ของมัน และเส้นไม่มีเส้นใดเปลี่ยน หมายความว่าคำตอบนี้มั่นคง ไม่สั่นคลอน',
  en_h='I Ching — #11 Peace',
  en='Your six lines stack heaven beneath earth, giving the calmest oracle in the entire book: Peace, Tai. Small departs, great arrives. Your flourishing was never about beating anyone; it is about arranging the small and the great so each sits where it belongs. Not a single changing line: this answer does not wobble.'),
 dict(no='8',
  th_h='ดาวเก้าเก่า + ทซอลกิน — ผู้ริเริ่มและผู้เร่งพายุ',
  th='ดาวประจำปีเกิดของคุณคือ Three Blue Wood ธาตุไม้สีน้ำเงิน ทะเยอทะยาน ตรงไป ไม่ชอบอ้อมค้อม ส่วนจักรวาลมายันบอกว่าคุณคือ Kin 239 Blue Storm เสียงที่ 5 แปลตรงตัวว่า คุณคือคนที่สร้างพายุแห่งการเปลี่ยนแปลงจากแกนกลางของตัวเอง แล้วกระจายมันออกไปให้คนอื่นหายใจได้มากขึ้น คนแบบคุณไม่กลัวการเปลี่ยนแปลง คนแบบคุณตายช้า ๆ ถ้าอยู่นิ่งเกินไป',
  en_h='Nine Star Ki + Dreamspell — initiator and storm',
  en='Your Nine Star Ki birth star is Three Blue Wood: bold, direct, allergic to detours. The Mayan count calls you Kin 239, Blue Overtone Storm. Read plainly: you generate storms of change from your own core and radiate them so others can breathe deeper. People like you do not fear change. People like you die slowly standing still.'),
])
# ==================== M — หน้า 4 (HD/kalachakra/cosmo) =================
m4 = ('ฮิวแมนดีไซน์ · กัลจักรทิเบต · จุดกึ่งกลาง', 'Human Design · Kalachakra · Cosmobiology', [
 dict(no='9',
  th_h='ฮิวแมนดีไซน์ — Generator 4/6 หัวใจอารมณ์',
  th='คุณคือ Generator พลังงานชีวิตของคุณมาจากงานที่คุณรัก ไม่ใช่งานที่คนอื่นบอกว่าดี และอำนาจตัดสินใจของคุณคืออารมณ์ กฎเดียวที่ต้องจำ: อย่าตัดสินใจบนยอดคลื่น รอให้น้ำนิ่งแล้วค่อยตอบ คำตอบที่มาจากความนิ่งไม่เคยทำให้คุณเสียใจ · โปรไฟล์ 4/6 บอกว่าโอกาสใหญ่ของชีวิตมาทางเพื่อนสนิทและเครือข่ายที่คุณสร้างด้วยความจริงใจ และครึ่งชีวิตหลังของคุณคือการเป็นแบบอย่างที่คนมาดูแล้วเชื่อ',
  en_h='Human Design — Generator 4/6, Emotional authority',
  en='You are a Generator: life energy flows from work you love, not work others praise. Your authority is emotional, and the single rule worth memorizing is this: never decide at the peak of the wave. Wait for still water, then answer. Answers born from calm never make you regret. Profile 4/6 says your biggest opportunities come through close friends and honestly built networks, and your second half of life becomes something people watch and believe.'),
 dict(no='10',
  th_h='กัลจักรทิเบต — วัวไฟหญิง เตาที่หลอมช้า',
  th='ปีทิเบตของคุณคือ Fire Ox female วัวไฟหญิง และสิ่งที่น่าทึ่งคือมันตรงกับ BaZi 丁丑 ของคุณข้ามระบบอย่างสมบูรณ์ สองตำราโบราณคนละแผ่นดินบอกเรื่องเดียวกัน: คุณคือเตาไฟที่หลอมทุกอย่างช้า ๆ ไม่ยอมแพ้ ไม่ลืม ไม่หนี',
  en_h='Kalachakra — Fire Ox female, the slow furnace',
  en='Tibetan year: Fire Ox female, matching your BaZi Ding-Chou perfectly across systems. Two ancient traditions from different lands agree: you are a fire furnace that smelts everything slowly, without surrender, without forgetting, without running.'),
 dict(no='11',
  th_h='จุดกึ่งกลาง — แกน "บ้าน" ที่ทุกอย่างหมุนรอบ',
  th='จุดกึ่งกลางอาทิตย์-จันทร์ของคุณอยู่กรกฎ 13.85° จุดที่ความตั้งใจและสัญชาตญาณบรรจบกัน มันชี้ไปที่คำเดียว: บ้าน ไม่ใช่บ้านเป็นตึก แต่คือที่ที่ใจสงบได้ มีคนที่ใช่ มีกลิ่นที่คุ้น ทุกความสำเร็จในดวงคุณจะไม่มีความหมายถ้าไม่มีที่แบบนี้ให้กลับไป',
  en_h='Cosmobiology — the axis called home',
  en='Your Sun/Moon midpoint rests at Cancer 13.85 sidereal, where conscious will meets instinct. It points at one word: home. Not a building. A place where the heart goes quiet, where the right people and familiar air live. Every success in your chart means nothing without somewhere like that to return to.'),
])
# ==================== M — หน้า 5 (fixed stars/sabian/synthesis) =================
m5 = ('ดาวฤกษ์หลวง · ซาเบียน · บทสรุป', 'Fixed Stars · Sabian · Synthesis', [
 dict(no='12',
  th_h='ซาเบียนดวงอาทิตย์ — ช่างทำรองเท้าสองคนที่โต๊ะเดียวกัน',
  th='ภาพจำของดวงคุณคือช่างทำรองเท้าสองคนนั่งทำงานเงียบ ๆ ข้างกัน ไม่มีใครแข่งกัน ไม่มีใครต้องเด่น ความเชี่ยวชาญเกิดจากการลงมือทำซ้ำทุกวัน และคุณค่าที่แท้มาจากงานฝีมือ ไม่ใช่เสียงปรบมือ นี่คือคำตอบว่าทำไมคุณรู้สึกเหนื่อยใจกับโลกที่ต้องโชว์ตัวตลอดเวลา เพราะดวงคุณไม่ได้มาจากตรงนั้น',
  en_h='Sabian Sun — two cobblers working at a table',
  en='The signature image of your chart: two craftsmen working quietly side by side. Nobody competing, nobody needing to be seen. Mastery grows from daily practice, and true worth lives in the craft itself, not the applause. This is why the always-performing world tires your heart: your chart never came from there.'),
 dict(no='13',
  th_h='บทสรุป — แก่นจาก 18 ศาสตร์',
  th='"เตาหลอมที่ทนไฟ — Generator ที่รักงานของตัวเอง ตัดสินใจเมื่อคลื่นอารมณ์นิ่งแล้ว Kin Blue Storm ผู้เร่งการเปลี่ยนแปลง Life Path 5 แห่งเสรีภาพ และแกนชีวิตคือบ้านกับคนที่ใช่"',
  en_h='Synthesis — the core from 18 sciences',
  en='"An old-soul furnace: a Generator who loves the work, deciding only when the emotional wave settles, a Blue Storm kin accelerating change, walking the freedom path of Life Path 5, with home and the right people as the axis everything turns on."'),
])
# ==================== Mai content =================
ma1 = ('DEEP NATAL READING', None, [
 dict(no='1',
  th_h='ลูกสาวของดวงอาทิตย์ — แสงที่สว่างขึ้นเมื่อเดินเข้ามา',
  th='ดวงอาทิตย์ของคุณอยู่สิงห์ ราศีของแสงและราชินี คุณคือคนที่ห้องสว่างขึ้นทันทีเมื่อเดินเข้ามา ไม่ใช่เพราะคุณพยายาม แต่เพราะมันเป็นธรรมชาติ แต่สิ่งที่คนอื่นไม่เคยเห็นคือจันทร์ของคุณอยู่กรกฎ ข้างในของคุณเป็นแม่ นุ่ม ลึก และรู้สึกได้มากกว่าที่ใบหน้ายิ้ม ๆ บอกไว้',
  en_h="A daughter of the Sun — the light that enters",
  en='Your Sun sits in Leo, the sign of light and queens. You are the person whose room brightens on arrival, not by effort but by nature. What others never see is your Cancer Moon: inside, you are a mother. Softer, deeper, feeling far more than the smiling face lets on.'),
 dict(no='2',
  th_h='ดาวฤกษ์หลวง — เส้นทางที่ยังว่างให้เขียน',
  th='ดวงของคุณไม่มีดาวฤกษ์หลวงใดเข้าเกณฑ์ 2 องศา คนฟังอาจคิดว่าเป็นเรื่องเศร้า แต่จริง ๆ ตรงกันข้าม เส้นทางของคุณไม่ถูกล็อกด้วยดาวดวงใดเลย คุณเขียนมันเองได้ทุกวัน อิสระแบบนี้หายากมาก และอย่าเสียมันไปกับการพยายามเป็นคนอื่น',
  en_h='Fixed stars — the road left blank on purpose',
  en='No royal star falls within two degrees in your chart. Some would call that sad; it is the opposite. Your route is not locked to any single star. You write it yourself, daily. Freedom like this is rare. Never spend it trying to become someone else.'),
])
ma2 = ('วงจรปี · ตถุดาว · ดาวเคราะห์น้อย', 'Year cycles · Zi Wei · Asteroids', [
 dict(no='3',
  th_h='วรรษผล — สองปีของการปลูกราก',
  th='ปี 2026 มุณฐะของคุณอยู่พฤษภ และดาวเสาร์เป็นเจ้าปี ปีของวินัย ความรับผิดชอบ และการวางรากที่จับต้องได้จริง อาจรู้สึกหนัก แต่รากที่ลงช่วงนี้จะติดดินจริง · ปี 2027 มุณฐะย้ายไปเมถุน เจ้าปียังเป็นเสาร์ การเรียนรู้ การสื่อสาร และคำที่เลือกใช้จะกลายเป็นเครื่องมือหลัก สองปีนี้คือช่วงปลูกรากให้ต้นที่จะใหญ่มากในอนาคต',
  en_h='Varshaphal — two root-growing years',
  en='2026 places your Muntha in Taurus with Saturn as year lord: discipline, responsibility, foundations you can actually touch. Heavy sometimes, but roots laid now grip for real. In 2027 Muntha moves to Gemini with Saturn still lord: learning, communication and chosen words become your main tools. Two seasons of growing roots for a very tall tree later.'),
 dict(no='4',
  th_h='ตถุดาว — วังชีวิตแห่งปีลิง',
  th='คุณเกิดเดือนจันทรคติหก วันที่ยี่สิบเก้า ชั่วโมง亥 วังชีวิตของคุณอยู่ที่ 申 ปีลิง ชีวิตของคุณคือนักแก้ปัญหาที่คล่องแคล่ว คิดไวกว่าที่สถานการณ์เปลี่ยน และมักเสนอทางออกก่อนที่คนอื่นจะเริ่มเข้าใจปัญหา',
  en_h='Zi Wei Dou Shu — Life Palace in the Monkey year',
  en='Born in lunar month six, day twenty-nine, at the Hai hour, your Life Palace sits in Shen, the Monkey. Your life reads as the agile problem-solver: thinking faster than circumstances shift, offering exits before others finish understanding the problem.'),
 dict(no='5',
  th_h='ไครอน — แผลเรื่องการถูกประเมินค่า',
  th='ไครอนของคุณเดินถอยหลังในธนู บาดแผลเก่าของคุณเกี่ยวกับการถูกตัดสินว่าไม่ดีพอ ไม่เก่งพอ ไม่ใช่แบบที่ควรจะเป็น แต่ฟังตรงนี้: คนที่เคยถูกประเมินค่าต่ำกว่าความจริง มักกลายเป็นคนที่มองเห็นคุณค่าของคนอื่นก่อนที่เขาจะเห็นมันในตัวเอง นี่คือของขวัญที่ซ่อนอยู่ คุณเห็นแสงในคนที่ยังไม่รู้ตัวว่ามีแสง',
  en_h='Chiron — the wound about being valued',
  en='Your Chiron walks retrograde through Sagittarius. The old wound is being judged: not good enough, not quite the right shape. But here is the truth: people once undervalued below their reality often become the ones who see other people\'s worth before those people see it themselves. That is the hidden gift. You see light in someone who has not yet noticed they glow.'),
])
ma3 = ('เลข · หยี่จิ๋ง · ดาวเก้า · ทซอลกิน', 'Numerology · I Ching · Nine Star Ki · Dreamspell', [
 dict(no='6',
  th_h='เลขศาสตร์ — เส้นทางนักเชื่อมใจ',
  th='Life Path ของคุณคือ 2 คุณเกิดมาเพื่อเชื่อมใจคน ประสาทสัมผัสของคุณจับอารมณ์คนอื่นได้ละเอียดกว่าคนทั่วไปหลายเท่า คู่หูคือคำที่อยู่ในชะตาของคุณอย่างสวยงาม คุณไม่ได้เกิดมาเพื่อเดินคนเดียว · ปี 2026 เป็น Personal Year 9 ปีแห่งการปล่อยวาง ปิดประตูเก่าอย่างสงบ แล้ว 2027 คือปีที่ 1 ปีเริ่มใหม่ด้วยมือของคุณเอง',
  en_h='Numerology — the heart-bridge path',
  en='Your Life Path is 2: born to bridge hearts. Your senses read other people\'s emotions far more finely than most. Partnership sits beautifully inside your destiny; you were never meant to walk alone. 2026 is a Personal Year 9, releasing old doors gently. Then 2027 is a 1 year: a new beginning started by your own hands.'),
 dict(no='7',
  th_h='หยี่จิ๋ง — เรื่องราวที่ยังเขียนไม่จบ',
  th='เมล็ดดวงของคุณชี้ไปที่หยี่จิ๋งหมายเลข 40 解 การปลดปล่อย และน่าทึ่งตรงที่มันสอดคล้องกับดวงทั้งใบ: หยี่จิ๋งของคุณคือเรื่องของการรอจังหวะที่ใช่ แล้วปลดปล่อยสิ่งที่เกาะกุมไว้นานเกิน คำตอบยังไม่ตายตัวเพราะบทของคุณยังถูกเขียนอยู่ โดยมือของคุณเอง',
  en_h='I Ching — the story still being written',
  en='Your birth-seed points to I Ching hexagram 40, Deliverance, which fits the whole chart: yours is the story of waiting for the right moment and letting go of what has been gripped too long. The answer is not fixed because your chapter is still being written, by your own hand.'),
 dict(no='8',
  th_h='ดาวเก้าเก่า + ทซอลกิน — นักสะสมและลิงน้ำเงิน',
  th='ดาวประจำปีเกิดของคุณคือ Eight White Earth ธาตุดิน คุณสะสมทรัพยาและความมั่นคงได้เก่งกว่าที่คนภายนอกเห็น ดูเบา แต่ข้างในจริงจัง · ส่วนจักรวาลมายันเรียกคุณว่า Kin 231 Blue Monkey เสียงที่ 10 ความสนุกของคุณคือเวทมนตร์จริง ๆ มันละลายความหนักหน่วงในห้องได้ทั้งห้อง',
  en_h='Nine Star Ki + Dreamspell — accumulator and Blue Monkey',
  en='Your Nine Star Ki star is Eight White Earth: steady, quietly skilled with resources, more serious inside than the outside shows. The Mayan count names you Kin 231, Blue Spectral Monkey: your playfulness is real magic, dissolving heaviness for an entire room.'),
])
ma4 = ('ฮิวแมนดีไซน์ · กัลจักรทิเบต · จุดกึ่งกลาง', 'Human Design · Kalachakra · Cosmobiology', [
 dict(no='9',
  th_h='ฮิวแมนดีไซน์ — Manifestor 2/4 หัวใจอารมณ์',
  th='คุณคือ Manifestor ผู้ริเริ่มที่ไม่ต้องรอใครอนุญาต พลังของคุณคือการเริ่มก่อนแล้วแจ้งให้คนรอบข้างรู้ ชีวิตจะไหลลื่นที่สุดเมื่อทำแบบนี้ ถ้ารอขออนุญาตจะอึดอัดจนเบื่อโลก · อำนาจตัดสินใจของคุณคืออารมณ์ อย่าตัดสินใจบนยอดคลื่น · โปรไฟล์ 2/4: พรสวรรค์ของคุณซ่อนอยู่และคนอื่นมองเห็นก่อนคุณเห็น และโอกาสครั้งใหญ่มาทางเพื่อนแท้เสมอ',
  en_h='Human Design — Manifestor 2/4, Emotional authority',
  en='You are a Manifestor, an initiator who waits for nobody\'s permission. Your power works like this: begin first, then inform the room, and life flows. Waiting for approval makes you ache until you resent the world. Your authority is emotional; never decide at the wave\'s peak. Profile 2/4: your talent hides until others spot it first, and big chances always arrive through true friends.'),
 dict(no='10',
  th_h='กัลจักรทิเบต — งูเหล็กหญิงผู้มองทะลุ',
  th='ปีทิเบตของคุณคือ Iron Snake female งูเหล็กหญิง งูเหล็กคือปัญญาที่เย็นตัวและมองทะลุสิ่งที่คนอื่นมองไม่เห็น พูดน้อย แต่เห็นต้นเหตุของทุกเรื่อง คนแบบนี้ไม่ชนะเกมเร็ว แต่ชนะเกมยาวเสมอ',
  en_h='Kalachakra — the Iron Snake (female)',
  en='Tibetan year: Iron Snake female. The Iron Snake is cool intelligence that sees through what others miss. Speaks little, sees root causes, always wins the long game.'),
 dict(no='11',
  th_h='จุดกึ่งกลาง — แกน "บ้านที่ใจสงบ"',
  th='ต้นไม้จุดกึ่งกลางของคุณมี 12 ภาพ (ยืนยัน ≤1° 8 ภาพ) โครงเรื่องจิตใต้สำนึกของคุณเน้นคำเดียวซ้ำ ๆ คือ ความมั่นคงของใจ ความปลอดภัยทางอารมณ์สำคัญกว่าความหรูหรา บ้านที่ใจสงบคือสิ่งที่คุณยอมแลกทุกอย่างเพื่อไปให้ถึง',
  en_h='Cosmobiology — the axis of inner safety',
  en='Your midpoint tree holds twelve pictures (eight confirmed within one degree). Your unconscious story repeats a single word over and over: inner stability. Emotional safety outranks luxury; a home where the heart is quiet is the one place you would trade anything to reach.'),
])
ma5 = ('ซาเบียน · บทสรุป', 'Sabian · Synthesis', [
 dict(no='12',
  th_h='ซาเบียนดวงอาทิตย์ — ราชินีน้อยแห่งเดคันของตัวเอง',
  th='ดวงอาทิตย์สิงห์ของคุณอยู่ในเดคันที่ราชินีทรงพลัง ความสง่างามของคุณไม่ใช่การโอ้อวด แต่คือการรู้ว่าแสงของตัวเองอยู่ตรงไหน และไม่ต้องขออนุญาตใครให้ส่องมันออกมา',
  en_h='Sabian Sun — the little queen of her own decan',
  en='Your Leo Sun sits in the regal decan: elegance is not showing off. It is knowing exactly where your light lives, and needing nobody\'s permission to let it out.'),
 dict(no='13',
  th_h='บทสรุป — แก่นจาก 18 ศาสตร์',
  th='"ดวงอาทิตย์ลูกสาวสิงห์ จันทร์แม่ผู้ดูแล Manifestor ผู้เริ่มก่อนด้วยหัวใจอารมณ์ Life Path 2 นักเชื่อมใจ Kin Blue Monkey ผู้ปลดปล่อยด้วยเสน่ห์ และงูเหล็กผู้มองทะลุถึงต้นเหตุ"',
  en_h='Synthesis — the core from 18 sciences',
  en='"A Leo daughter of the Sun with a mother-Moon; a Manifestor initiating with emotional clarity; a Life Path 2 heart-bridge; a Blue Monkey dissolving spells with charm; an Iron Snake seeing straight to the root."'),
])

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf_lib import render_pages



class _C:
    pass

import pdf_lib as _pl

def render_pages(fname, person_th, person_en, birth_line, pages):
    # create canvas here since pdf_lib expects one passed in
    from reportlab.pdfgen import canvas as _canvas
    c = _canvas.Canvas(fname, pagesize=(595.2755905511812, 841.8897637795277))
    _pl.render_pages(c, fname, person_th, person_en, birth_line, pages)

render_pages(OUT_M, 'การอ่านดวงชะตาเจาะลึก — ของคุณ', 'M', 'M · 1997-05-19 · 05:45 · Chonburi, Thailand',
             [m1, m2, m3, m4, m5])
render_pages(OUT_MA, 'การอ่านดวงชะตาเจาะลึก — ของไหม', 'Mai', 'Mai · 2001-08-18 · 22:32 · Nonthaburi, Thailand',
             [ma1, ma2, ma3, ma4, ma5])
