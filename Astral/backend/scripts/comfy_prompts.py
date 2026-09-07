"""Prompt map for ComfyUI AI art generation (premium Thai astrology+tarot PDF).

Style: classical oil-painting / illuminated-manuscript luxury, deep indigo-plum
+ gold-leaf palette, real depth. Negative: flat/low-res/watermark/modern/photo/
text/letters/UI.

Each PROMPT_<KEY> / NEG_<KEY> pair matches assets/ai-art/<key>_final.png where
<key> is the value returned by build_combined_premium._art_key(card_name).
"""
# Cover / decor (Helios) — key: cover
PROMPT_COVER = ("Masterpiece classical oil painting, HELIOS the sun god driving a golden "
                "CHARIOT pulled by two rising sun-horses across a deep indigo starry night "
                "sky, radiant divine sun-crown light, ornate Baroque gold-leaf frame, "
                "mythological, ethereal, highly detailed, dramatic chiaroscuro, intricate, "
                "sharp focus, hyperdetailed, fine art print, Museum quality")
NEG_COVER = ("malformed hands, fused fingers, vacant eyes, flat, text, letters, watermark, "
             "modern, photo, low resolution, CGI, cartoon, simple, blurry")

# Major arcana keys used by _art_key()
PROMPT_DEVIL = ("Rider-Waite Tarot card 'The Devil': central Baphomet with goat head and "
                "bat wings, glowing inverted pentagram on the forehead, standing on a "
                "rectangular stone pedestal, a naked man and a naked woman chained by the "
                "neck to the pedestal below him, one raised torch in each hand, ornate "
                "gilded card border, dark indigo and gold, classical fine-art oil painting, "
                "symmetrical, sharp focus, hyperdetailed")
NEG_DEVIL = ("throne, king, royal, bird wings, missing pentagram, no humans, no chains, "
             "extra arms, malformed hands, fused fingers, vacant eyes, text, letters, "
             "watermark, modern, photo, low resolution, cartoon, minimal, CGI, blurry")

PROMPT_WORLD = ("Traditional Tarot card 'The World': a serene dancing figure inside a large "
                "wreath circle, four living creatures (angel, eagle, bull, lion) in the "
                "corners holding the four elements, ornate gilded card border, dark indigo "
                "and gold mystical palette, classical fine-art oil painting, sharp focus, "
                "hyperdetailed, symmetric, ethereal completion and wholeness")
NEG_WORLD = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
             "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_STAR = ("Traditional Tarot card 'The Star': a naked woman kneeling by a pool, pouring "
               "water from two jugs onto land and water, a large eight-pointed star above "
               "with seven smaller stars, calm night sky, ornate gilded card border, dark "
               "indigo and gold mystical palette, classical fine-art oil painting, sharp "
               "focus, hyperdetailed, symmetric, hope and serenity")
NEG_STAR = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
            "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_SUN = ("Traditional Tarot card 'The Sun': a large radiant sun with a human face "
              "shining over a walled garden, a naked child riding a white horse holding a "
              "red banner, sunflowers, ornate gilded card border, dark indigo and gold "
              "mystical palette, classical fine-art oil painting, sharp focus, hyperdetailed, "
              "symmetric, warm joy and vitality")
NEG_SUN = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
           "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_MOON = ("Traditional Tarot card 'The Moon': a full moon with a serene face shedding "
               "two drips of dew, a dog and a wolf howling below, a crawfish emerging from "
               "water, a winding path between two towers, night sky, ornate gilded card "
               "border, dark indigo and gold mystical palette, classical fine-art oil "
               "painting, sharp focus, hyperdetailed, symmetric, mystery and dream")
NEG_MOON = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
            "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_TOWER = ("Traditional Tarot card 'The Tower': a tall stone tower struck by lightning, "
                "crown exploding off, two figures falling from the tower, flames and "
                "scattered gold coins, dark stormy sky, ornate gilded card border, dark "
                "indigo and gold mystical palette, classical fine-art oil painting, sharp "
                "focus, hyperdetailed, dramatic destruction")
NEG_TOWER = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
             "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_LOVERS = ("Traditional Tarot card 'The Lovers': a naked man and woman beneath a "
                 "radiant angel with outstretched arms, behind them the Tree of Life and "
                 "the Tree of Knowledge with serpent, ornate gilded card border, dark "
                 "indigo and gold mystical palette, classical fine-art oil painting, sharp "
                 "focus, hyperdetailed, symmetric, sacred union")
NEG_LOVERS = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
              "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_FOOL = ("Traditional Tarot card 'The Fool': a young traveler in bright attire at a "
               "cliff edge with a small dog, a bindle and a white rose, mountains and sky "
               "behind, ornate gilded card border, dark indigo and gold mystical palette, "
               "classical fine-art oil painting, sharp focus, hyperdetailed, new beginning")
NEG_FOOL = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
            "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_MAGICIAN = ("Traditional Tarot card 'The Magician': a robed figure standing at an "
                   "altar with the four suit symbols (cup, pentacle, sword, wand) above, "
                   "one hand raised to heaven one pointing down, infinity symbol above his "
                   "head, ornate gilded card border, dark indigo and gold mystical palette, "
                   "classical fine-art oil painting, sharp focus, hyperdetailed, power")
NEG_MAGICIAN = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
                "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_PRIESTESS = ("Traditional Tarot card 'The High Priestess': a seated woman between "
                    "two pillars (black and white) with a veil, crescent moon at her feet, "
                    "scroll, ornate gilded card border, dark indigo and gold mystical "
                    "palette, classical fine-art oil painting, sharp focus, hyperdetailed, "
                    "mystery and intuition")
NEG_PRIESTESS = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
                 "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_EMPRESS = ("Traditional Tarot card 'The Empress': a crowned woman seated in a lush "
                  "garden of wheat and stream, holding a scepter, Venus symbol, ornate "
                  "gilded card border, dark indigo and gold mystical palette, classical "
                  "fine-art oil painting, sharp focus, hyperdetailed, abundance and nature")
NEG_EMPRESS = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
               "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_EMPEROR = ("Traditional Tarot card 'The Emperor': a bearded crowned man on a stone "
                  "throne with ram motifs, holding an ankh and scepter, mountains behind, "
                  "ornate gilded card border, dark indigo and gold mystical palette, "
                  "classical fine-art oil painting, sharp focus, hyperdetailed, authority")
NEG_EMPEROR = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
               "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_HIEROPHANT = ("Traditional Tarot card 'The Hierophant': a religious figure seated "
                     "between two pillars, holding a triple cross, two acolytes before him, "
                     "ornate gilded card border, dark indigo and gold mystical palette, "
                     "classical fine-art oil painting, sharp focus, hyperdetailed, tradition")
NEG_HIEROPHANT = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
                  "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_CHARIOT = ("Traditional Tarot card 'The Chariot': a triumphant figure standing in a "
                  "chariot drawn by two sphinxes (black and white), canopy of stars, "
                  "ornate gilded card border, dark indigo and gold mystical palette, "
                  "classical fine-art oil painting, sharp focus, hyperdetailed, willpower")
NEG_CHARIOT = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
               "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_STRENGTH = ("Traditional Tarot card 'Strength': a gentle woman closing the jaws of a "
                   "lion with infinite patience, infinity symbol above her head, ornate "
                   "gilded card border, dark indigo and gold mystical palette, classical "
                   "fine-art oil painting, sharp focus, hyperdetailed, courage and calm")
NEG_STRENGTH = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
                "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_HERMIT = ("Traditional Tarot card 'The Hermit': an old sage with a lantern holding a "
                 "staff on a mountain peak under stars, ornate gilded card border, dark "
                 "indigo and gold mystical palette, classical fine-art oil painting, sharp "
                 "focus, hyperdetailed, solitude and wisdom")
NEG_HERMIT = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
              "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_WHEEL = ("Traditional Tarot card 'Wheel of Fortune': a large wheel with symbols and "
                "creatures (angel, eagle, bull, lion) at the corners, a sphinx atop, "
                "ornate gilded card border, dark indigo and gold mystical palette, classical "
                "fine-art oil painting, sharp focus, hyperdetailed, fate and cycles")
NEG_WHEEL = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
             "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_JUSTICE = ("Traditional Tarot card 'Justice': a seated figure holding scales in one "
                  "hand and a sword in the other, crown and veil, ornate gilded card border, "
                  "dark indigo and gold mystical palette, classical fine-art oil painting, "
                  "sharp focus, hyperdetailed, truth and fairness")
NEG_JUSTICE = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
               "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_HANGED = ("Traditional Tarot card 'The Hanged Man': a serene figure suspended upside "
                 "down by one foot from a living tree, halo of light around the head, "
                 "ornate gilded card border, dark indigo and gold mystical palette, "
                 "classical fine-art oil painting, sharp focus, hyperdetailed, surrender")
NEG_HANGED = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
              "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_DEATH = ("Traditional Tarot card 'Death': a armored reaper on a white horse holding "
                "a black flag with a white rose, a fallen king, bishop and child before him, "
                "ornate gilded card border, dark indigo and gold mystical palette, classical "
                "fine-art oil painting, sharp focus, hyperdetailed, transformation")
NEG_DEATH = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
             "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_TEMPERANCE = ("Traditional Tarot card 'Temperance': an angel with two cups pouring "
                     "water between them, one foot on land one in water, a path to a crown "
                     "in the distance, ornate gilded card border, dark indigo and gold "
                     "mystical palette, classical fine-art oil painting, sharp focus, "
                     "hyperdetailed, balance")
NEG_TEMPERANCE = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
                  "cartoon, minimal, CGI, blurry, text, letters, watermark")

PROMPT_JUDGEMENT = ("Traditional Tarot card 'Judgement': an angel blowing a trumpet above "
                    "rising figures emerging from coffins, ocean and mountains, ornate "
                    "gilded card border, dark indigo and gold mystical palette, classical "
                    "fine-art oil painting, sharp focus, hyperdetailed, rebirth")
NEG_JUDGEMENT = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
                 "cartoon, minimal, CGI, blurry, text, letters, watermark")

# Minor arcana fallback — key derived from card name (e.g. six_of_pentacles).
# Used when no major-specific prompt exists; keep generic but on-style.
PROMPT_MINOR = ("Traditional Tarot card, ornate gilded card border, dark indigo and gold "
                "mystical palette, classical fine-art oil painting, symbolic imagery, sharp "
                "focus, hyperdetailed, symmetric, ethereal")
NEG_MINOR = ("malformed hands, fused fingers, vacant eyes, extra limbs, modern, photo, "
             "cartoon, minimal, CGI, blurry, text, letters, watermark")
