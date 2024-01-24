from bs4 import BeautifulSoup

def parse_html(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    
    result = []
    current_label = None
    
    for tag in soup.find_all(['p', 'div']):
        text = tag.get_text(strip=True)
        
        if tag.has_attr('style'):
            styles = tag['style'].lower()
            
            if 'text-align:center' in styles:
                if text.isupper():
                    current_label = 'Character'
                elif '(' in text and ')' in text:
                    current_label = 'Paranthetical'
                else:
                    current_label = 'Dialogue'
            elif 'text-align:right' in styles:
                if text.endswith(':'):
                    current_label = 'Action'
                else:
                    raise ValueError(f"Invalid right-aligned text: {text}")
            elif 'text-align:left' in styles:
                if text.upper().startswith(('INT', 'EXT')):
                    current_label = 'Scene Heading'
        
        elif tag.name == 'strong' and text.isupper():
            current_label = 'Scene Heading'
            
        elif tag.name == 'i':
            current_label = 'Transition'
            
        elif tag.name == 'em':
            current_label = 'Shot'
            
        if current_label and text:
            result.append((current_label, text))
    
    return result

# Example usage
html_text = """
<p>INT. CAR.--NIGHT</p>
<p>.A COUPLE DRIVING A CAR FROM PONDY TO , IN CAR RADIO SONG PLAYS</p>
<p style="text-align: center;">HUSBAND<br>Single road, double roadnu mari mari varuthu, vandi otavey Kadapa iruku</p>
<p>In radio song ends and rj speaks to a caller&nbsp;</p>
<p style="text-align: center;">RJ(V.O.)<br>Hello name intha ulagathuleyay ungaluku pudicha idam yethu nu sollunga</p>
<p style="text-align: center;">HUSBAND<br>Intha papera dashboard la veiyu</p>
<p>Wife takes the divorce hearing document and puts it in the dashboardps</p>
<p style="text-align: center;">RJ(V.O.) Seri apadina ungaluku maraka mudiyatha negalvu nadantha yedamnu soldringa</p>
<p style="text-align: center;">HUSBAND</p>
<p style="text-align: center;">&nbsp;Un favorite place yenna</p>
<p style="text-align: center;">WIFE</p>
<p style="text-align: center;">Yen unaku theriyatha</p>
<p style="text-align: center;">HUSBAND</p>
<p style="text-align: center;">Yenna pudacha appo antha name roof top resto-barnu solluva, ippo mariduchanu ketan</p>
<p style="text-align: center;">WIFE</p>
<p style="text-align: center;">yethavathu pesanumney pesuviya</p>
<p style="text-align: center;">HUSBAND</p>
<p style="text-align: center;">venna na sollatha, athuvum illama court la we should live together for four months as husband and wife nu solli irukanga, so i asked</p>
<p style="text-align: center;">WIFE</p>
<p style="text-align: center;">court kaga than pesiriya, appo na unaku divorce venum nu soli irukalam la, anga matum yen, yen wife vitu iruka mudiyathu nu katharana</p>
<p style="text-align: center;">HUSBAND</p>
<p style="text-align: center;">Unnakaga than ippo uruguranga, nee yari yenaku divorce kudukarthuku, innum oru 6-8 monthla onsite poiduvan, aparom yaru kuda vena orru mei, athu veraikum ulunga iru</p>
<p style="text-align: center;">WIFE</p>
<p style="text-align: center;">Psyco, nee laam thirundhave matta</p>
<p style="text-align: center;">HUSBAND</p>
<p style="text-align: center;">Psyco va nee than di psyco, un appan psyco, un annan psyco, un friend nu soldiyey oruthan avan psyco</p>
"""

try:
    parsed_result = parse_html(html_text)
    
    for label, text in parsed_result:
        print(f"{label}: {text}")
except ValueError as e:
    print(f"Error: {e}")
