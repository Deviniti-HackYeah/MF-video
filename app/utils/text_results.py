import os
import json
import asyncio

from app.utils.llm_analyzer import LLMAnalyzer
from app.utils.functions import write_to_file_with_lock

class TextResults:
    def __init__(self, cache_dir, user_id, session, data_dir):
        self.cache_dir = cache_dir
        self.user_id = user_id
        self.session = session
        self.data_dir = data_dir
    
    def __str__(self):
        return "Answering text tasks with LLM"
    
    async def clarity_check(self, text):
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
                
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                # print(bielik_response)
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena zrozumiałości przekazu"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "clarity_check.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "clarity_check.json"), {})
            return {}
            
    async def readibility_check(self, text, readibility_metrics):
        "miary prostego języka: gunning fog, indeks czytelności flescha"
        
        prompt = f"""
            Przeprowadź analizę czytelności poniższego tekstu. Skorzystaj z miar takich jak Gunning Fog Index, Flesch Reading Ease oraz innych wskaźników oceniających poziom trudności i przystępność tekstu. Uwzględnij następujące elementy:
            Gunning Fog Index: Oceń, jaki poziom wykształcenia jest wymagany do pełnego zrozumienia treści.
            Flesch Reading Ease: Określ stopień zrozumiałości tekstu na skali od 0 do 100, gdzie wyższe wartości oznaczają łatwiejszy do przyswojenia tekst.
            Flesch-Kincaid Grade Level: Oszacuj odpowiedni poziom szkolny dla tego tekstu.     
            Wyniki przedstaw z krótkim opisem, co oznaczają poszczególne wartości w kontekście czytelności i trudności tekstu.
            
            Wartości mertyk: {readibility_metrics}
        """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Miary czytelności tekstu"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "readibility_measures.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "readibility_measures.json"), {})
            return {}
        
    async def sentiment_check(self, text):
        "analiza sentymentu wypowiedzi"
        
        prompt = """
            Przeanalizuj podany tekst, określając jego sentyment oraz wykrywając emocje i ton wypowiedzi. Uwzględnij poniższe elementy:
            Sentyment: Czy tekst jest pozytywny, neutralny, czy negatywny?
            Emocje: Jakie emocje są wyrażone w tekście (np. radość, gniew, smutek, zaskoczenie, strach, pogarda)?
            Ton wypowiedzi: Czy wypowiedź ma ton formalny, neutralny, agresywny, ironiczny, wesoły, poważny, itp.?
            Hate speech: Czy tekst zawiera mowę nienawiści lub wyrażenia obraźliwe skierowane do grupy lub jednostki? Jeśli tak, określ charakter wypowiedzi i zidentyfikuj ewentualne obraźliwe treści.
        """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Sentyment wypowiedzi"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "sentiment.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "sentiment.json"), {})
            return {}
          
    async def short_summary_check(self, text):
        "krótkie tekstowe podsumowanie wypowiedzi w języku polskim – co zostało zrozumiane przez odbiorcę (kluczowe przekazy)"
        
        prompt = """
            Przeanalizuj poniższy tekst i wygeneruj krótkie podsumowanie w języku polskim, które opisze kluczowe przekazy, 
            jakie mogły zostać zrozumiane przez odbiorcę. Skup się na najważniejszych informacjach, które wypływają z wypowiedzi, 
            unikając nadmiernych szczegółów i cytatów. Wynik powinien być zwięzły, trafny i odzwierciedlać główne myśli przekazane w tekście.
        """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                # ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                # final_response = json.loads(final_response)
                # if type(final_response) == dict:
                #     final_response["area"] = "Sentyment wypowiedzi"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "short_sumamry.json"), {"short_summary": bielik_response})      
                return bielik_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "short_sumamry.json"), {})
            return {}
           
    async def structure_check(self, text):
        "ocena struktury tekstu: czy zachowane zostały wstęp, rozwinięcie i zakończnie"
        
        prompt = """Przeanalizuj podany tekst, aby ocenić jego strukturę. Zidentyfikuj, czy występuje w nim logiczny wstęp, rozwinięcie oraz zakończenie. 
            Opisz, w jaki sposób każdy z tych elementów został zrealizowany. Wskaż, czy poszczególne części są spójne i płynnie przechodzą jedna w drugą. 
            Udziel odpowiedzi w formie:
            Wstęp: Opis tego, czy i jak został zrealizowany wstęp oraz jaki ma charakter (np. wprowadzający, problemowy, narracyjny).
            Rozwinięcie: Czy rozwinięcie rozbudowuje główny temat i zawiera kluczowe argumenty oraz szczegóły? Jakie są jego mocne i słabe strony?
            Zakończenie: Opisz, czy i jak zostało zrealizowane zakończenie, czy jest ono podsumowaniem całości i wyciąga wnioski z treści rozwinięcia.
        """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena struktury tekstu"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "text_structure.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "text_structure.json"), {})
            return {}
        
    async def target_group_check(self, text, target_groups, target_education):
        "ocena grupy docelowej wypowiedzi"
        
        prompt = f"""
            Przeanalizuj podany tekst w celu określenia grupy docelowej omawianego nagrania pod kątem grupy wiekowej oraz poziomu wykształcenia odbiorców. 
            Zwróć uwagę na styl języka, używane słownictwo, omawiane tematy oraz wszelkie kontekstowe wskazówki sugerujące docelową demografię. Następnie porównaj
            to z informacjami o grupie docelowej, które zostały dostarczone w opisie zadania. Czy tekst jest dostosowany do odbiorców z podanego 
            zakresu/zakresów wiekowych: {target_groups} oraz poziomu/poziomów wykształcenia: {target_education}?
            Przedstaw ocenę wraz z krótkim uzasadnieniem.
        """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena struktury tekstu"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "target_group.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "target_group.json"), {})
            return {}
        
    async def language_and_foreign_words_check(self, text):
        "ocena języka i wtrąceń w innych jezykach niż polski"
        prompt = """
            Przeanalizuj poniższy tekst i oceń, czy jest on w pełni napisany w języku polskim. 
            W przypadku wystąpienia słów, fraz lub wyrażeń w innym języku (np. angielskim, niemieckim, francuskim itp.), zidentyfikuj te fragmenty i wskaż, w jakim języku zostały napisane. 
            Wynik przedstaw jako jedną z opcji: 'Tekst w pełni po polsku', 'Występują słowa lub frazy w innym języku' oraz wypisz znalezione fragmenty z przypisaniem języka.
            Jeśli tekst jest w pełni po polsku, daj maksymalną ocenę i nie dawaj żadnych rekomendacji (tj. wpisz '-'),
            jeśli zawiera wtrącenia w innym języku, na podstawie ich liczby określ, czy mogą wpłynąć na zrozumienie tekstu i odpowiednio obniż ocenę.
            Przykładowy tekst do analizy: "Spotkajmy się na lunch w przyszłym tygodniu. BTW, I'll confirm the date later."
            Oczekiwany wynik: "Występują słowa lub frazy w innym języku: 'BTW, I'll confirm the date later' - angielski.
            """
            
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena języka i wtrąceń w innych językach"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "language_rate.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "language_rate.json"), {})
            return {}   
        
    async def overall_taking_style(self, text, metrics):
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
            
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena ogólnej jakości wypowiedzi"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "overall_rating.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            return {}
        
    async def pause_quality_analysis(self, text): # , pause_count, total_pause_time, total_talking_time
        "ocena występowania przerw w wypowiedzi"
   
        prompt = f"""
            Dostarczony tekst to transkrypcja wypowiedzi mówcy (w formie listy). Przeanalizuj ją pod kątem początku i końca danego fragmentu wypowiedzi. Jeśli różnica pomiędzy czasem zakończenia
            danego fragmentu a czasem rozpoczęcia kolejnego fragmentu wynosi więcej niż sekundę (czyli długość przerwy między fragmentami jest większa niż 1 sekunda), oznacza to
            niechcianą pauzę w wypowiedzi. Zidentyfikuj takie przerwy i określ ich długość w sekundach oraz wskaż czas w jakim taka przerwa się zaczyna i w jakim kończy. 
            Następnie ocen, czy przerwy wpływają na płynność wypowiedzi, czy są zbyt długie
            lub zbyt częste. Wskaz, czy przerwy są związane z błędami językowymi, takimi jak wahania, powtórzenia, użycie wypełniaczy (np. "yyy", "eee") , które mogą wynikać z długich
            lub częstych przerw. Przedstaw szczegółową ocenę, wskazując obszary do poprawy oraz pozytywne elementy wypowiedzi.
            """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, str(text), max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response, pause=True, text=str(text))
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena ciągłości wypowiedzi (występowanie przerw)"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "pause_check.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "pause_check.json"), {})
            return {}
        
    async def prolongation_check(self, text):
        "ocena przeciągłości wypowiadania słów"
 
        prompt = f"""
            Dostarczony tekst to transkrypcja wypowiedzi mówcy (w formie listy). Przeanalizuj ją pod kątem początku i końca danego fragmentu wypowiedzi. Jeśli różnica pomiędzy czasem rozpoczęcia
            danego fragmentu a czasem zakończenia tego fragmentu wynosi więcej niż 0.8 sekundy (czyli długość wypowiedzi danego słowa jest większa niż 0.8 sekundy), oznacza to,
            że mówca przeciąga wypowiadanie danego słowa. Zidentyfikuj takie fragmenty i określ ich długość w sekundach. Następnie ocen, czy przeciąganie wypowiadania słów wpływa
            na płynność wypowiedzi, czy są zbyt długie lub zbyt częste. Wskaz, czy przeciąganie wypowiadania słów jest związane z błędami językowymi, takimi jak wahania, powtórzenia,
            użycie wypełniaczy (np. "yyy", "eee"), które mogą wynikać z długich lub częstych przerw. 
            Przedstaw szczegółową ocenę, wskazując obszary do poprawy oraz pozytywne elementy wypowiedzi.
            """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, str(text), max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response, prolongation=True, text=str(text))
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena przeciągłości wypowiadania słów"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "prolongation_check_check.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "prolongation_check.json"), {})
            return {}   
        
    async def topic_check(self, text):
        "sprawdzanie zmiany tematu wypowiedzi"
        
        prompt = f"""
            Przeanalizuj poniższy tekst pod kątem spójności tematycznej. 
            Zidentyfikuj, czy w trakcie wypowiedzi nastąpiła zmiana głównego tematu. 
            Wskaż, od którego momentu lub zdania nastąpiła zmiana, a także określ pierwotny oraz nowy temat. 
            Uwzględnij różnice w kontekście i treści, które wskazują na odejście od pierwotnego wątku rozmowy.
            """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena zmiany tematu wypowiedzi (spójność tematyczna)"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "topic_change.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "topic_change.json"), {})
            return {} 
        
    async def false_words_check(self, text, word_dict):
        "sprawdzenie niepoprawnych/nieistniejących słów w wypowiedzi lub zwrotów nie mających sensu np. słona wata cukrowa"
        
        prompt = f"""
            Przeanalizuj poniższy tekst pod kątem występowania niepoprawnych/nieistniejących słów lub zwrotów nie mających sensu (np. słona wata cukrowa lub sucha woda) 
            bądź niewłaściwie użytych związków frazeologicznych. Zidentyfikuj takie fragmenty i wskaż, w jaki sposób mogą wpłynąć na zrozumienie tekstu.
            """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response, false_words=True, text=str(word_dict))
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena niepoprawnych/nieistniejących słów/zwrotów w wypowiedzi"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "false_words.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "false_words.json"), {})
            return {} 
        
    async def variety_of_statements_check(self, text):
        "sprawdzenie różnorodności wypowiedzi (powtarzanie tych samych słów, fraz)"
        
        prompt = f"""
            Przeanalizuj poniższy tekst pod kątem różnorodności wypowiedzi. Zidentyfikuj, czy w tekście występuje powtarzanie tych samych słów, fraz lub zdań.
            Określ, czy powtarzanie jest celowe (np. w celu podkreślenia ważnych informacji) czy przypadkowe (np. wynikające z braku zróżnicowania w słownictwie).
            Wskaż, jakie słowa, frazy lub związki frazeologiczne powtarzają się najczęściej i jakie mogą być tego przyczyny.
            Oceń, czy powtarzanie wpływa na zrozumienie tekstu i czy może być uznane za wadę wypowiedzi.
            """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena różnorodności wypowiedzi"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "variety_of_statements.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "variety_of_statements.json"), {})
            return {} 
        
    async def active_form_check(self, text):
        "sprawdzenie czy wypowiedź jest w formie czynnej, czy nie ma za dużo zdań w stronie biernej"
        
        prompt = f"""
            Przeanalizuj poniższy tekst pod kątem formy gramatycznej. Zidentyfikuj, czy wypowiedź jest w formie czynnej, 
            czy zawiera zbyt wiele zdań w stronie biernej (użyte słowa np. podano, wskazano, podsumowano).
            Określ, czy użycie formy biernej jest uzasadnione (np. w celu podkreślenia roli obiektu w zdaniu) czy niepotrzebne (np. wynikające z braku zróżnicowania w konstrukcjach zdaniowych).
            Wskaż, jakie słowa, frazy lub związki frazeologiczne sugerują, że wypowiedź jest w formie biernej i jakie mogą być tego przyczyny.
            Oceń, czy użycie formy biernej wpływa na zrozumienie tekstu i czy może być uznane za wadę wypowiedzi.
            """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena formy gramatycznej wypowiedzi (aktywna/bierna)"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "active_form_check.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "active_form_check.json"), {})
            return {} 
        
    async def clarity_of_information_check(self, text):

        "sprawdzenie czy wypowiedź jest jasna i zrozumiała, czy nie zawiera np. za dużo liczb, skrótów, terminów"
        
        prompt = f"""
            Przeanalizuj poniższy tekst pod kątem jasności przekazu. Zidentyfikuj, czy wypowiedź jest napisana w sposób zrozumiały dla odbiorcy,
            czy zawiera zbyt wiele skrótów, terminów, liczb lub specjalistycznych wyrażeń. Określ, czy użycie skrótów i terminów jest uzasadnione
            (np. w celu skrócenia tekstu lub podkreślenia specyficznych informacji) czy niepotrzebne (np. wynikające z braku zrozumienia odbiorcy).
            Wskaż, jakie słowa, frazy lub związki frazeologiczne sugerują, że wypowiedź jest trudna do zrozumienia i jakie mogą być tego przyczyny.
            Oceń, czy użycie skrótów i terminów wpływa na zrozumienie tekstu i czy może być uznane za wadę wypowiedzi.
            """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena jasności przekazu wypowiedzi (zrozumiałość)"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "clarity_of_information_check.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "clarity_of_information_check.json"), {})
            return {}
        
    async def interjections_and_anecdotes_check(self, text):
        "sprawdzenie czy w wypowiedzi występują zbędne wtrącenia, anegdoty, niepotrzebne opisy"
        
        prompt = f"""
            Przeanalizuj poniższy tekst pod kątem wtrąceń i anegdot. Zidentyfikuj, czy wypowiedź zawiera zbyt wiele wtrąceń, anegdot, niepotrzebnych opisów lub zbędnych informacji.
            Określ, czy użycie wtrąceń i anegdot jest uzasadnione (np. w celu urozmaicenia tekstu lub podkreślenia ważnych informacji) 
            czy niepotrzebne (np. wynikające z braku zróżnicowania w konstrukcjach zdaniowych).
            Wskaż, jakie słowa, frazy lub związki frazeologiczne sugerują, że wypowiedź zawiera zbyt wiele wtrąceń i anegdot oraz jakie mogą być tego przyczyny.
            Oceń, czy użycie wtrąceń i anegdot wpływa na zrozumienie tekstu i czy może być uznane za wadę wypowiedzi.
            """
        
        llm = LLMAnalyzer(self.cache_dir)
        ok, bielik_response, error = llm.send_to_chat("bielik", prompt, text, max_tokens=2000, temperature=0.1)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena wtrąceń i anegdot w wypowiedzi"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "interjections_and_anecdotes_check.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "interjections_and_anecdotes_check.json"), {})
            return {} 