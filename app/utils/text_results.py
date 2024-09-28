from app.utils.llm_analyzer import LLMAnalyzer

class TextAnswers:
    def __init__(self):
        pass
    
    def __str__(self):
        return "Answering text tasks with LLM"
    
    
    def clarity_check(self, text, cache_dir):
        "Ocena zrozumiałości przekazu"
        
        prompt = """
            Przeanalizuj poniższy tekst i oceń jego zrozumiałość. Weź pod uwagę następujące kryteria:
            Jasność przekazu: Czy tekst jest napisany w sposób zrozumiały dla odbiorcy? Czy używane są proste i jednoznaczne wyrażenia?
            Logika i spójność: Czy poszczególne fragmenty tekstu są logicznie powiązane? Czy tekst jest uporządkowany i konsekwentny?
            Dostosowanie do grupy docelowej: Czy styl, ton i język są odpowiednie dla grupy docelowej?
            Unikanie zbędnego żargonu: Czy tekst unika nadmiernego stosowania specjalistycznych terminów?
            Podaj ogólną ocenę zrozumiałości w skali od 1 do 5 (1 - bardzo trudny do zrozumienia, 5 - bardzo zrozumiały) i uzasadnij swoją ocenę, wskazując konkretne 
            elementy wpływające na zrozumiałość przekazu.
            """
                
        llm = LLMAnalyzer(cache_dir)
        ok, response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                print(response)            
                return response
            
        except Exception as e:
            print(f"Error: {e}")
            return ""
            
        
    def readibility_check(self, text, readibility_metrics):
        "miary prostego języka: gunning fog, indeks czytelności flescha"
        
        prompt = f"""
            Przeprowadź analizę czytelności poniższego tekstu. Skorzystaj z miar takich jak Gunning Fog Index, Flesch Reading Ease oraz innych wskaźników oceniających poziom trudności i przystępność tekstu. Uwzględnij następujące elementy:
            Gunning Fog Index: Oceń, jaki poziom wykształcenia jest wymagany do pełnego zrozumienia treści.
            Flesch Reading Ease: Określ stopień zrozumiałości tekstu na skali od 0 do 100, gdzie wyższe wartości oznaczają łatwiejszy do przyswojenia tekst.
            Flesch-Kincaid Grade Level: Oszacuj odpowiedni poziom szkolny dla tego tekstu.     
            Wyniki przedstaw z krótkim opisem, co oznaczają poszczególne wartości w kontekście czytelności i trudności tekstu.
            
            Wartości mertyk: {readibility_metrics}
        """
        
        llm = LLMAnalyzer(cache_dir)
        ok, response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                print(response)            
                return response
            
        except Exception as e:
            print(f"Error: {e}")
            return ""
        
        
    def sentiment_check(self, text):
        "analiza sentymentu wypowiedzi"
        
        prompt = """
            Przeanalizuj podany tekst, określając jego sentyment oraz wykrywając emocje i ton wypowiedzi. Uwzględnij poniższe elementy:
            Sentyment: Czy tekst jest pozytywny, neutralny, czy negatywny?
            Emocje: Jakie emocje są wyrażone w tekście (np. radość, gniew, smutek, zaskoczenie, strach, pogarda)?
            Ton wypowiedzi: Czy wypowiedź ma ton formalny, neutralny, agresywny, ironiczny, wesoły, poważny, itp.?
            Hate speech: Czy tekst zawiera mowę nienawiści lub wyrażenia obraźliwe skierowane do grupy lub jednostki? Jeśli tak, określ charakter wypowiedzi i zidentyfikuj ewentualne obraźliwe treści.
        """
        
        llm = LLMAnalyzer(cache_dir)
        ok, response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                print(response)            
                return response
            
        except Exception as e:
            print(f"Error: {e}")
            return ""
        
        
    def short_summary_check(self, text):
        "krótkie tekstowe podsumowanie wypowiedzi w języku polskim – co zostało zrozumiane przez odbiorcę (kluczowe przekazy)"
        
        prompt = """
            Przeanalizuj poniższy tekst i wygeneruj krótkie podsumowanie w języku polskim, które opisze kluczowe przekazy, 
            jakie mogły zostać zrozumiane przez odbiorcę. Skup się na najważniejszych informacjach, które wypływają z wypowiedzi, 
            unikając nadmiernych szczegółów i cytatów. Wynik powinien być zwięzły, trafny i odzwierciedlać główne myśli przekazane w tekście.
        """
        
        llm = LLMAnalyzer(cache_dir)
        ok, response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                print(response)            
                return response
            
        except Exception as e:
            print(f"Error: {e}")
            return ""
        
        
    def structure_check(self, text):
        "ocena struktury tekstu: czy zachowane zostały wstęp, rozwinięcie i zakończnie"
        
        prompt = """Przeanalizuj podany tekst, aby ocenić jego strukturę. Zidentyfikuj, czy występuje w nim logiczny wstęp, rozwinięcie oraz zakończenie. 
            Opisz, w jaki sposób każdy z tych elementów został zrealizowany. Wskaż, czy poszczególne części są spójne i płynnie przechodzą jedna w drugą. 
            Udziel odpowiedzi w formie:
            Wstęp: Opis tego, czy i jak został zrealizowany wstęp oraz jaki ma charakter (np. wprowadzający, problemowy, narracyjny).
            Rozwinięcie: Czy rozwinięcie rozbudowuje główny temat i zawiera kluczowe argumenty oraz szczegóły? Jakie są jego mocne i słabe strony?
            Zakończenie: Opisz, czy i jak zostało zrealizowane zakończenie, czy jest ono podsumowaniem całości i wyciąga wnioski z treści rozwinięcia.
        """
        
        llm = LLMAnalyzer(cache_dir)
        ok, response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                print(response)            
                return response
            
        except Exception as e:
            print(f"Error: {e}")
            return ""
        
        
    def target_group_check(self, text):
        "ocena grupy docelowej wypowiedzi"
        
        prompt = """
            Przeanalizuj podany tekst w celu określenia grupy docelowej omawianego nagrania pod kątem grupy wiekowej oraz poziomu wykształcenia odbiorców. 
            Zwróć uwagę na styl języka, używane słownictwo, omawiane tematy oraz wszelkie kontekstowe wskazówki sugerujące docelową demografię. 
            Przedstaw ocenę wraz z krótkim uzasadnieniem.
        """
        
        llm = LLMAnalyzer(cache_dir)
        ok, response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                print(response)            
                return response
            
        except Exception as e:
            print(f"Error: {e}")
            return ""
        
    def language_and_foreign_words_check(self, text):
        "ocena języka i wtrąceń w innych jezykach niż polski"
        prompt = """
            Przeanalizuj poniższy tekst i oceń, czy jest on w pełni napisany w języku polskim. 
            W przypadku wystąpienia słów, fraz lub wyrażeń w innym języku (np. angielskim, niemieckim, francuskim itp.), zidentyfikuj te fragmenty i wskaż, w jakim języku zostały napisane. 
            Wynik przedstaw jako jedną z opcji: 'Tekst w pełni po polsku', 'Występują słowa lub frazy w innym języku' oraz wypisz znalezione fragmenty z przypisaniem języka."
            Przykładowy tekst do analizy: "Spotkajmy się na lunch w przyszłym tygodniu. BTW, I'll confirm the date later."
            Oczekiwany wynik: "Występują słowa lub frazy w innym języku: 'BTW, I'll confirm the date later' - angielski.
            """
            
        llm = LLMAnalyzer(cache_dir)
        ok, response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                print(response)            
                return response
            
        except Exception as e:
            print(f"Error: {e}")
            return ""   
        
    
    def overall_taking_style(self, text, metrics):
        "ogólna ocena jakości wypowiedzi mówcy z uwzględnieniem metryk"
        
        prompt = f"""
            Oceń jakość i tempo wypowiedzi na podstawie poniższych metryk oraz treści dostarczonego tekstu. Uwzględnij następujące wskaźniki:
            Total Talking Time: Łączny czas mówienia w sekundach.
            Pause Count: Liczba pauz podczas mówienia.
            Total Pause Time: Łączny czas pauz w sekundach.
            Word Count: Liczba wypowiedzianych słów.
            Words per Second: Liczba słów wypowiedzianych na sekundę.
            Letter Count: Łączna liczba liter w tekście.
            Readability Scores:
            Gunning Fog: Wskaźnik trudności zrozumienia tekstu na podstawie liczby trudnych słów.
            Flesch Reading Ease: Im wyższy wynik, tym łatwiejszy tekst do zrozumienia (optymalny przedział 60-70).
            Flesch-Kincaid Grade Level: Odpowiedni poziom trudności dla danego poziomu edukacji (optymalny: 7-9).
            Dale-Chall Readability Score: Im wyższy wynik, tym trudniejszy tekst (optymalny poniżej 8).
            Kryteria oceny:
            Jakość mówienia:
            Klarowność: Czy tekst jest łatwy do zrozumienia przy podanych wskaźnikach trudności? Oceń na podstawie metryk Flesch Reading Ease i Gunning Fog.
            Płynność: Czy liczba pauz i ich łączny czas (Total Pause Time) są odpowiednie w stosunku do całkowitego czasu mówienia (Total Talking Time)?
            Intonacja: Oceń, czy rozmieszczenie pauz i zmiany tempa wspierają zrozumienie tekstu.
            Tempo mówienia:
            Zbyt szybkie: Czy Words per Second przekracza 2,0 WPS, co może wpływać na trudność w odbiorze?
            Zbyt wolne: Czy Words per Second jest poniżej 1,0 WPS, co może powodować utratę uwagi?
            Optymalne: Tempo w przedziale 1,0-2,0 WPS, z pauzami proporcjonalnymi do złożoności tekstu.
            Czytelność:
            Oceń, czy podane wskaźniki (Flesch Reading Ease, Flesch-Kincaid Grade Level, Dale-Chall Readability Score) sugerują, że tekst jest dostosowany do odbiorców (optymalny: średni poziom trudności).
            Wynik: Przydziel ocenę w skali od 1 do 10 dla każdego kryterium, uwzględniając, czy mówca dostosował tempo, płynność i klarowność wypowiedzi do poziomu trudności tekstu. Zaproponuj konkretne sugestie poprawy, jeśli zauważysz obszary wymagające optymalizacji.
            
            Metryki: {metrics}
            
            """
            
        llm = LLMAnalyzer(cache_dir)
        ok, response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                print(response)            
                return response
            
        except Exception as e:
            print(f"Error: {e}")
            return ""
        
    
    def pause_quality_analysis(self, text, pause_count, total_pause_time, total_talking_time):
        "ocena "
        
        prompt = f"""
            Przeanalizuj dostarczone nagranie przy użyciu następujących metryk: 'pause_count' oraz 'total_pause_time'. Oceń jakość wypowiedzi w oparciu o te wskaźniki, biorąc pod uwagę następujące aspekty:
            Przerwy:
            Liczba przerw (pause_count).
            Łączny czas przerw (total_pause_time w sekundach).
            Łączny czas wypowiedzi (total_talking_time).
            Płynność Wypowiedzi:
            Sprawdź, czy przerwy wpływają na płynność mówienia, np. czy są zbyt częste lub trwają zbyt długo.
            Błędy Językowe:
            Wykryj możliwe błędy językowe, takie jak wahania, powtórzenia, użycie wypełniaczy (np. "yyy", "eee"), które mogą wynikać z długich lub częstych przerw.
            Przedstaw szczegółową ocenę, wskazując obszary do poprawy oraz pozytywne elementy wypowiedzi.
            
            Pause count: {pause_count} 
            Total pause time: {total_pause_time} sekund
            Total talking time: {total_talking_time} sekund
            """
        
        llm = LLMAnalyzer(cache_dir)
        ok, response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                print(response)            
                return response
            
        except Exception as e:
            print(f"Error: {e}")
            return ""   
        
        
# ta = TextAnswers()

# text = "W obniżeniu ulega oprocentowanie oferowanych obligacji przy jednoczesnym zachowaniu preferencji dla rynku detalicznego względem rynku hurtowego, dedykowanego inwestorom instytucjonalnym."
# # text = "Kiedy poszliśmy na brunch po meetingu, okazało się że ten John to całkiem fajny gość."
# cache_dir = "cache"
# readibility_metrics = "'gunning_fog': 24.44, 'flesch_reading_ease': 1.43, 'flesch_kincaid_grade_level': 17.8, 'dale_chall_readibility_score': 19.54"
# metrics = "{'total_talking_time': 18.0, 'pause_count': 3, 'total_pause_time': 2.84, 'word_count': 23, 'words_per_second': 1.2777777777777777, 'letter_count': 166, 'readibility': {'gunning_fog': 24.44, 'flesch_reading_ease': 1.43, 'flesch_kincaid_grade_level': 17.8, 'dale_chall_readibility_score': 19.54}}"

# ta.clarity_check(text, cache_dir)
# ta.readibility_check(text, readibility_metrics)
# ta.sentiment_check(text)
# ta.short_summary_check(text)
# ta.structure_check(text)
# ta.target_group_check(text)
# ta.language_and_foreign_words_check(text)
# ta.overall_taking_style(text, metrics)
# ta.pause_quality_analysis(text, 3, "2.84s", 18)