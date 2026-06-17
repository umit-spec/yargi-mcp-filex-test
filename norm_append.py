# -*- coding: utf-8 -*-
"""Faz 3 — idempotent norm ekleyici (dev aracı)."""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\FilexAI\Filex\src-tauri\resources\norms_seed.json"

LAWS = {
    "HMK": ("Hukuk Muhakemeleri Kanunu",
            "https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6100&MevzuatTur=1&MevzuatTertip=5",
            "2011-02-04"),
    "IIK": ("İcra ve İflas Kanunu",
            "https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=2004&MevzuatTur=1&MevzuatTertip=3",
            "1932-06-19"),
    "TK":  ("Tebligat Kanunu",
            "https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=7201&MevzuatTur=1&MevzuatTertip=3",
            "1959-02-19"),
}


def clean(md):
    lines = [l for l in md.split("\n") if "#_ftnref" not in l]
    md = "\n".join(lines)
    md = re.sub(r"\[\\?\[?\d+\\?\]?\]\(#_ftn\d+\)", "", md)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md


ARTICLES = [
    ("IIK", "68/a", r"""**c) İtirazın geçici olarak kaldırılması:**

**Madde 68/a – (Ek: 18/2/1965-538/39 md.)**

**(Değişik birinci fıkra: 17/7/2003-4949/17 md.)** Takibin dayandığı senet hususî olup, imza itiraz sırasında borçlu tarafından reddedilmişse, alacaklı itirazın kendisine tebliği tarihinden itibaren altı ay içinde itirazın geçici olarak kaldırılmasını isteyebilir. Bu hâlde icra hâkimi iki taraftan izahat alır.

Tatbika medar imza mevcutsa bununla, yoksa borçluya yazdıracağı yazı ve attıracağı imza ile yapılacak mükayese ve incelemelerden veya diğer delil ve karinelerden icra mahkemesi, reddedilen imzanın borçluya aidiyetine kanaat getirirse itirazın muvakkaten kaldırılmasına karar verir.

**(Değişik: 9/11/1988-3494/3 md.)** İcra hakimi, imzanın borçluya aidiyetine karar verdiği takdirde borçluyu sözü edilen senede dayanan takip konusu alacağın yüzde onu oranında para cezasına mahkum eder. Borçlu, borçtan kurtulma, menfi tespit veya istirdat davası açarsa, bu para cezasının infazı dava sonuna kadar tehir olunur."""),

    ("HMK", "119", r"""**Dava dilekçesinin içeriği**

**MADDE 119-** (1) Dava dilekçesinde aşağıdaki hususlar bulunur:

a) Mahkemenin adı.

b) Davacı ile davalının adı, soyadı ve adresleri.

c) Davacının Türkiye Cumhuriyeti kimlik numarası.

ç) Varsa tarafların kanuni temsilcilerinin ve davacı vekilinin adı, soyadı ve adresleri.

d) Davanın konusu ve malvarlığı haklarına ilişkin davalarda, dava konusunun değeri.

e) Davacının iddiasının dayanağı olan bütün vakıaların sıra numarası altında açık özetleri.

f) İddia edilen her bir vakıanın hangi delillerle ispat edileceği.

g) Dayanılan hukuki sebepler.

ğ) Açık bir şekilde talep sonucu.

h) Davacının, varsa kanuni temsilcisinin veya vekilinin imzası.

(2) Birinci fıkranın (a), (d), (e), (f) ve (g) bentleri dışında kalan hususların eksik olması hâlinde, hâkim davacıya eksikliği tamamlaması için bir haftalık kesin süre verir. Bu süre içinde eksikliğin tamamlanmaması hâlinde dava açılmamış sayılır."""),

    ("HMK", "124", r"""**Tarafta iradî değişiklik**

**MADDE 124-** (1) Bir davada taraf değişikliği, ancak karşı tarafın açık rızası ile mümkündür.

(2) Bu konuda kanunlarda yer alan özel hükümler saklıdır.

(3) Ancak, maddi bir hatadan kaynaklanan veya dürüstlük kuralına aykırı olmayan taraf değişikliği talebi, karşı tarafın rızası aranmaksızın hâkim tarafından kabul edilir.

(4) Dava dilekçesinde tarafın yanlış veya eksik gösterilmesi kabul edilebilir bir yanılgıya dayanıyorsa, hâkim karşı tarafın rızasını aramaksızın taraf değişikliği talebini kabul edebilir. Bu durumda hâkim, davanın tarafı olmaktan çıkarılan ve aleyhine dava açılmasına sebebiyet vermeyen kişi lehine yargılama giderlerine hükmeder."""),

    ("HMK", "176", r"""**Kapsamı ve sayısı**

**MADDE 176-** (1) Taraflardan her biri, yapmış olduğu usul işlemlerini kısmen veya tamamen ıslah edebilir.

(2) Aynı davada, taraflar ancak bir kez ıslah yoluna başvurabilir."""),

    ("HMK", "177", r"""**MADDE 177-** (1) Islah, tahkikatın sona ermesine kadar yapılabilir.

(2) **(Ek:22/7/2020-7251/18 md.)** Yargıtayın bozma kararından veya bölge adliye mahkemesinin kaldırma kararından sonra dosya ilk derece mahkemesine gönderildiğinde, ilk derece mahkemesinin tahkikata ilişkin bir işlem yapması hâlinde tahkikat sona erinceye kadar da ıslah yapılabilir. Ancak bozma kararına uymakla ortaya çıkan hukuki durum ortadan kaldırılamaz.

(3) Islah, sözlü veya yazılı olarak yapılabilir. Karşı taraf duruşmada hazır değilse veya ıslah talebi duruşma dışında yapılıyorsa, bu yazılı talep veya tutanak örneği, haber vermek amacıyla karşı tarafa bildirilir."""),

    ("HMK", "189", r"""**MADDE 189-** (1) Taraflar, kanunda belirtilen süre ve usule uygun olarak ispat hakkına sahiptir.

(2) Hukuka aykırı olarak elde edilmiş olan deliller, mahkeme tarafından bir vakıanın ispatında dikkate alınamaz.

(3) Kanunun belirli delillerle ispatını emrettiği hususlar, başka delillerle ispat olunamaz.

(4) Bir vakıanın ispatı için gösterilen delilin caiz olup olmadığına mahkemece karar verilir."""),

    ("HMK", "190", r"""**İspat yükü**

**MADDE 190-** (1) İspat yükü, kanunda özel bir düzenleme bulunmadıkça, iddia edilen vakıaya bağlanan hukuki sonuçtan kendi lehine hak çıkaran tarafa aittir.

(2) Kanuni bir karineye dayanan taraf, sadece karinenin temelini oluşturan vakıaya ilişkin ispat yükü altındadır. Kanunda öngörülen istisnalar dışında, karşı taraf, kanuni karinenin aksini ispat edebilir."""),

    ("HMK", "194", r"""**Somutlaştırma yükü ve delillerin gösterilmesi**

**MADDE 194-** (1) Taraflar, dayandıkları vakıaları, ispata elverişli şekilde somutlaştırmalıdırlar.

(2) Tarafların, dayandıkları delilleri ve hangi delilin hangi vakıanın ispatı için gösterildiğini açıkça belirtmeleri zorunludur."""),

    ("HMK", "297", r"""**Hükmün kapsamı**

**MADDE 297-** (1) Hüküm "Türk Milleti Adına" verilir ve bu ibareden sonra aşağıdaki hususları kapsar:

a) Hükmü veren mahkeme ile hâkim veya hâkimlerin ve zabıt kâtibinin ad ve soyadları ile sicil numaraları, mahkeme çeşitli sıfatlarla görev yapıyorsa hükmün hangi sıfatla verildiğini.

b) Tarafların ve davaya katılanların kimlikleri ile Türkiye Cumhuriyeti kimlik numarası, varsa kanuni temsilci ve vekillerinin ad ve soyadları ile adreslerini.

c) Tarafların iddia ve savunmalarının özetini, anlaştıkları ve anlaşamadıkları hususları, çekişmeli vakıalar hakkında toplanan delilleri, delillerin tartışılması ve değerlendirilmesini, sabit görülen vakıalarla bunlardan çıkarılan sonuç ve hukuki sebepleri.

ç) Hüküm sonucu, yargılama giderleri ile taraflardan alınan avansın harcanmayan kısmının iadesi, varsa kanun yolları ve süresini.

d) Hükmün verildiği tarih ve hâkim veya hâkimlerin ve zabıt kâtibinin imzalarını.

e) Gerekçeli kararın yazıldığı tarihi.

(2) Hükmün sonuç kısmında, gerekçeye ait herhangi bir söz tekrar edilmeksizin, taleplerden her biri hakkında verilen hükümle, taraflara yüklenen borç ve tanınan hakların, sıra numarası altında; açık, şüphe ve tereddüt uyandırmayacak şekilde gösterilmesi gereklidir."""),

    ("HMK", "304", r"""**Hükmün tashihi**

**MADDE 304-** (1) Hükümdeki yazı ve hesap hataları ile diğer benzeri açık hatalar, mahkemece resen veya taraflardan birinin talebi üzerine düzeltilebilir. Hüküm tebliğ edilmişse hâkim, tarafları dinlemeden hatayı düzeltemez. Davet üzerine taraflar gelmezse, dosya üzerinde inceleme yapılarak karar verilebilir.

(2) Tashih kararı verildiği takdirde, düzeltilen hususlarla ilgili karar, mahkemede bulunan nüshalar ile verilmiş olan suretlerin altına veya bunlara eklenecek ayrı bir kâğıda yazılır, imzalanır ve mühürlenir."""),

    ("HMK", "305", r"""**Hükmün tavzihi**

**MADDE 305-** (1) Hüküm yeterince açık değilse veya icrasında tereddüt uyandırıyor yahut birbirine aykırı fıkralar içeriyorsa, icrası tamamlanıncaya kadar taraflardan her biri hükmün açıklanmasını veya tereddüt ya da aykırılığın giderilmesini isteyebilir.

(2) Hüküm fıkrasında taraflara tanınan haklar ve yüklenen borçlar, tavzih yolu ile sınırlandırılamaz, genişletilemez ve değiştirilemez.

**Hükmün tamamlanması — MADDE 305/A- (Ek:22/7/2020-7251/27 md.)** (1) Taraflardan her biri, nihaî kararın tebliğinden itibaren bir ay içinde, yargılamada ileri sürülmesine veya kendiliğinden hükme geçirilmesi gerekli olmasına rağmen hakkında tamamen veya kısmen karar verilmeyen hususlarda, ek karar verilmesini isteyebilir."""),

    ("HMK", "345", r"""**Başvuru süresi**

**MADDE 345-** (1) İstinaf yoluna başvuru süresi iki haftadır. Bu süre, ilamın usulen taraflardan her birine tebliğiyle işlemeye başlar. İstinaf yoluna başvuru süresine ilişkin özel kanun hükümleri saklıdır."""),

    ("HMK", "353", r"""**Duruşma yapılmadan verilecek kararlar**

**MADDE 353-** (1) Ön inceleme sonunda dosyada eksiklik bulunmadığı anlaşılırsa;

a) Aşağıdaki durumlarda bölge adliye mahkemesi, esası incelemeden kararın kaldırılmasına ve davanın yeniden görülmesi için dosyanın kararı veren mahkemeye veya kendi yargı çevresinde uygun göreceği başka bir yer mahkemesine ya da görevli ve yetkili mahkemeye gönderilmesine duruşma yapmadan kesin olarak karar verir:

1) Davaya bakması yasak olan hâkimin karar vermiş olması.

2) İleri sürülen haklı ret talebine rağmen reddedilen hâkimin davaya bakmış olması.

3) Mahkemenin görevli ve yetkili olmasına rağmen görevsizlik veya yetkisizlik kararı vermiş olması veya mahkemenin görevli ya da yetkili olmamasına rağmen davaya bakmış bulunması.

4) Diğer dava şartlarına aykırılık bulunması.

5) Mahkemece usule aykırı olarak davanın veya karşı davanın açılmamış sayılmasına, davaların birleştirilmesine veya ayrılmasına karar verilmiş olması.

6) **(Değişik:22/7/2020-7251/35 md.)** Mahkemece, uyuşmazlığın çözümünde etkili olabilecek ölçüde önemli delillerin toplanmamış veya değerlendirilmemiş olması ya da talebin önemli bir kısmı hakkında karar verilmemiş olması.

b) Yargılamada eksiklik bulunmamakla beraber esas yönünden duruşma yapılmadan başvurunun esastan reddine veya düzelterek yahut yeniden esas hakkında karar verilir."""),

    ("HMK", "355", r"""**İncelemenin kapsamı**

**MADDE 355-** (1) İnceleme, istinaf dilekçesinde belirtilen sebeplerle sınırlı olarak yapılır. Ancak, bölge adliye mahkemesi kamu düzenine aykırılık gördüğü takdirde bunu resen gözetir."""),

    ("HMK", "361", r"""**Temyiz edilebilen kararlar**

**MADDE 361-** (1) Bölge adliye mahkemesi hukuk dairelerinden verilen temyizi kabil nihai kararlar ile hakem kararlarının iptali talebi üzerine verilen kararlara karşı tebliğ tarihinden itibaren iki hafta içinde temyiz yoluna başvurulabilir.

(2) Davada haklı çıkmış olan taraf da hukuki yararı bulunmak şartıyla temyiz yoluna başvurabilir."""),

    ("TK", "10", r"""**Bilinen adreste tebligat:**

**Madde 10 –** Tebligat, tebliğ yapılacak şahsa bilinen en son adresinde yapılır.

**(Ek fıkra: 11/1/2011-6099/3 md.)** Bilinen en son adresin tebligata elverişli olmadığının anlaşılması veya tebligat yapılamaması hâlinde, muhatabın adres kayıt sisteminde bulunan yerleşim yeri adresi, bilinen en son adresi olarak kabul edilir ve tebligat buraya yapılır.

Şu kadar ki; kendisine tebliğ yapılacak şahsın müracaatı veya kabulü şartiyle her yerde tebligat yapılması caizdir."""),

    ("TK", "16", r"""**Aynı konutta oturan kişilere veya hizmetçiye tebligat:**

**Madde 16- (Değişik: 19/3/2003-4829/2 md.)**

Kendisine tebliğ yapılacak şahıs adresinde bulunmazsa tebliğ kendisi ile aynı konutta oturan kişilere veya hizmetçilerinden birine yapılır."""),

    ("TK", "23", r"""**Tebliğ mazbatası:**

**Madde 23 –** Tebliğ bir mazbata ile tevsik edilir. Bu mazbatanın:

1. Tebliği çıkaran merciin adını,

2. Tebliği istiyen tarafın adını, soyadını ve adresini,

3. Tebliğ olunacak şahsın adını, soyadını ve adresini,

4. Tebliğin mevzuunu,

5. Tebliğin kime yapıldığını ve tebliğ muhatabından başkasına yapılmış ise o kimsenin adını, soyadını, adresini ve 22 nci madde gereğince tebellüğe ehil olduğunu,

6. Tebliğin nerede ve ne zaman yapıldığını,

7. 21 inci maddedeki durumun tahaddüsü halinde bu hususlara mütaallik muamelenin yapıldığını, adreste bulunmama ve imtina için gösterilen sebebi,

8. **(Ek: 11/1/2011-6099/6 md.)** Tebligatın adres kayıt sistemindeki adrese yapılması durumunda buna ilişkin kaydı,

9. Tebliğ evrakı kime verilmiş ise onun imzası ile tebliğ memurunun adı, soyadı ve imzasını,

İhtiva etmesi lazımdır."""),

    ("TK", "25/a", r"""**Siyasî temsilcilik aracılığıyla yabancı ülkedeki Türk vatandaşlarına tebligat:**

**Madde 25/a- (Ek: 19/3/2003-4829/8 md.)**

Yabancı ülkede kendisine tebliğ yapılacak kimse Türk vatandaşı olduğu takdirde tebliğ o yerdeki Türkiye Büyükelçiliği veya Konsolosluğu aracılığıyla da yapılabilir.

Bu hâlde bildirimi Türkiye Büyükelçiliği veya Konsolosluğu veya bunların görevlendireceği bir memur yapar.

Tebliğin konusu ile hangi merci tarafından çıkarıldığı bilgilerinin yer aldığı ve otuz gün içinde başvurulmadığı takdirde tebliğin yapılmış sayılacağı ihtarını içeren bildirim, muhataba o ülkenin mevzuatının izin verdiği yöntemle gönderilir.

Bildirimin o ülkenin mevzuatına göre muhataba tebliğ edildiği belgelendirildiğinde, tebliğ tarihinden itibaren otuz gün içinde Türkiye Büyükelçiliği veya Konsolosluğuna başvurulmadığı takdirde tebligat otuzuncu günün bitiminde yapılmış sayılır."""),

    ("TK", "32", r"""**Usulüne aykırı tebliğin hükmü:**

**Madde 32 –** Tebliğ usulüne aykırı yapılmış olsa bile, muhatabı tebliğe muttali olmuş ise muteber sayılır.

Muhatabın beyan ettiği tarih, tebliğ tarihi addolunur."""),
]


def main():
    with open(OUT, encoding="utf-8") as f:
        records = json.load(f)
    seen = {(r["title"], r["articleNo"]) for r in records}
    added = 0
    for law_key, article_no, raw in ARTICLES:
        title, url, date = LAWS[law_key]
        key = (title, article_no)
        if key in seen:
            continue
        records.append({
            "normLevel": "N0",
            "title": title,
            "articleNo": article_no,
            "source": "mevzuat_mcp",
            "sourceUrl": url,
            "officialDate": date,
            "fullText": clean(raw),
        })
        seen.add(key)
        added += 1
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print("added %d, total now %d" % (added, len(records)))


if __name__ == "__main__":
    main()
