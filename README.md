# Library Catalog SOAP Web Service

Python SOAP web service pro uceni testovani SOAP API v SoapUI.

## Quick Start

### Predpoklady
- Docker a Docker Compose
- SoapUI (stahnout z https://www.soapui.org/)

### Spusteni sluzby

```bash
# Prejit do adresare projektu
cd SOAP

# Spustit sluzby (PostgreSQL + SOAP aplikace)
docker-compose up -d

# Sledovat logy
docker-compose logs -f soap_app
```

Sluzba je pripravena, kdyz vidis:
```
Library Catalog SOAP Service
============================================================
Service endpoint: http://0.0.0.0:8000/
WSDL available at: http://0.0.0.0:8000/?wsdl
```

### WSDL URL
```
http://localhost:8000/?wsdl
```

---

## Pouziti se SoapUI

### Krok 1: Vytvorit novy SOAP projekt
1. Otevrit SoapUI
2. File -> New SOAP Project
3. Project Name: `Library Catalog`
4. Initial WSDL: `http://localhost:8000/?wsdl`
5. Kliknout OK

SoapUI automaticky importuje WSDL a vygeneruje sablony pro vsechny operace.

### Krok 2: Prehled operaci

| Operace | Popis | Vstup | Vystup |
|---------|-------|-------|--------|
| GetBook | Ziskat knihu podle ID | book_id | Book |
| GetAllBooks | Seznam vsech knih | - | ArrayOfBook |
| AddBook | Pridat novou knihu | BookInput | Book |
| UpdateBook | Upravit knihu | book_id, BookInput | Book |
| DeleteBook | Smazat knihu | book_id | boolean |
| SearchBooks | Vyhledat knihy | query, genre | ArrayOfBook |
| BorrowBook | Vypujcit knihu | book_id, borrower_name | BorrowResult |
| ReturnBook | Vratit knihu | book_id | boolean |

### Krok 3: Testovani operaci

#### GetBook - Ziskat knihu
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:cat="http://library.example.com/catalog">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:GetBook>
         <cat:book_id>1</cat:book_id>
      </cat:GetBook>
   </soapenv:Body>
</soapenv:Envelope>
```

#### GetAllBooks - Seznam vsech knih
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:cat="http://library.example.com/catalog">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:GetAllBooks/>
   </soapenv:Body>
</soapenv:Envelope>
```

#### AddBook - Pridat knihu
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:cat="http://library.example.com/catalog"
                  xmlns:typ="http://library.example.com/types">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:AddBook>
         <cat:book>
            <typ:title>Clean Code</typ:title>
            <typ:author>Robert C. Martin</typ:author>
            <typ:isbn>978-0132350884</typ:isbn>
            <typ:year>2008</typ:year>
            <typ:genre>Programming</typ:genre>
         </cat:book>
      </cat:AddBook>
   </soapenv:Body>
</soapenv:Envelope>
```

#### SearchBooks - Vyhledat knihy
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:cat="http://library.example.com/catalog">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:SearchBooks>
         <cat:query>gatsby</cat:query>
         <cat:genre>Fiction</cat:genre>
      </cat:SearchBooks>
   </soapenv:Body>
</soapenv:Envelope>
```

#### BorrowBook - Vypujcit knihu
```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:cat="http://library.example.com/catalog">
   <soapenv:Header/>
   <soapenv:Body>
      <cat:BorrowBook>
         <cat:book_id>1</cat:book_id>
         <cat:borrower_name>Jan Novak</cat:borrower_name>
      </cat:BorrowBook>
   </soapenv:Body>
</soapenv:Envelope>
```

---

## Testovani SOAP Faults (chyb)

SOAP Faults jsou strukturovane chybove odpovedi. Libi se mi, jak se lisi od REST:
- REST: HTTP status kod (404, 400, 500)
- SOAP: Vzdy HTTP 200/500, detaily chyby v XML SOAP Fault

### BookNotFoundFault
Volej GetBook s neexistujicim ID:
```xml
<cat:GetBook>
   <cat:book_id>9999</cat:book_id>
</cat:GetBook>
```

Odpoved:
```xml
<soap11env:Fault>
   <faultcode>Client.BookNotFound</faultcode>
   <faultstring>Book with ID 9999 was not found in the catalog.</faultstring>
</soap11env:Fault>
```

### BookNotAvailableFault
Knihy s ID 4 a 8 jsou uz vypujcene (viz seed data). Zkus je vypujcit:
```xml
<cat:BorrowBook>
   <cat:book_id>4</cat:book_id>
   <cat:borrower_name>Test User</cat:borrower_name>
</cat:BorrowBook>
```

### InvalidInputFault
Volej AddBook bez povinnych poli:
```xml
<cat:AddBook>
   <cat:book>
      <typ:title></typ:title>
      <typ:author>Some Author</typ:author>
      <typ:isbn>123</typ:isbn>
   </cat:book>
</cat:AddBook>
```

### DuplicateISBNFault
Pridej knihu s ISBN, ktere uz existuje:
```xml
<cat:AddBook>
   <cat:book>
      <typ:title>Duplicate Book</typ:title>
      <typ:author>Someone</typ:author>
      <typ:isbn>978-0743273565</typ:isbn>  <!-- Uz existuje! -->
   </cat:book>
</cat:AddBook>
```

---

## Vytvoreni Test Suite v SoapUI

### 1. Vytvorit TestSuite
1. Prave kliknout na projekt -> New TestSuite
2. Pojmenovat: "Library Catalog Tests"

### 2. Pridat TestCase
1. Prave kliknout na TestSuite -> New TestCase
2. Pojmenovat: "GetBook Tests"

### 3. Pridat Test Step
1. Prave kliknout na TestCase -> Add Step -> SOAP Request
2. Vybrat operaci (GetBook)
3. Vyplnit request

### 4. Pridat Assertions

#### XPath Match Assertion
- Pravym klikem na response -> Add Assertion -> XPath Match
- XPath: `//Book/title`
- Expected: `The Great Gatsby`

#### Contains Assertion
- Add Assertion -> Contains
- Content: `Fitzgerald`

#### SOAP Fault Assertion
- Pro testovani chyb: Add Assertion -> SOAP Fault
- Ocekava SOAP Fault response

#### Not SOAP Fault Assertion
- Pro uspesne odpovedi: Add Assertion -> Not SOAP Fault

---

## SOAP vs REST: Klicove rozdily

| Aspekt | SOAP | REST |
|--------|------|------|
| Protokol | XML protokol | Architektonicky styl |
| Transport | HTTP, SMTP, atd. | Pouze HTTP |
| Format | Pouze XML | JSON, XML, atd. |
| Kontrakt | WSDL (striktni) | OpenAPI (volitelne) |
| Operace | Slovesne (GetBook) | Zdroje (GET /books/1) |
| Chyby | SOAP Faults | HTTP status kody |
| Typovani | Striktni (XSD) | Volne |
| Discovery | WSDL auto-generace | Dokumentace |

### Proc se SOAP stale pouziva?
1. **Enterprise systemy** - banky, pojistovny, vlady
2. **WS-Security** - zabudovana bezpecnost
3. **Transakce** - ACID pres vice systemu
4. **Striktni kontrakty** - zadne prekvapeni v datech

---

## Ukazkova data

V databazi je 8 knih:

| ID | Titul | Autor | Dostupna |
|----|-------|-------|----------|
| 1 | The Great Gatsby | F. Scott Fitzgerald | Ano |
| 2 | To Kill a Mockingbird | Harper Lee | Ano |
| 3 | 1984 | George Orwell | Ano |
| 4 | Pride and Prejudice | Jane Austen | Ne (John Smith) |
| 5 | The Catcher in the Rye | J.D. Salinger | Ano |
| 6 | Brave New World | Aldous Huxley | Ano |
| 7 | The Hobbit | J.R.R. Tolkien | Ano |
| 8 | Dune | Frank Herbert | Ne (Jane Doe) |

---

## Zastaveni sluzby

```bash
# Zastavit kontejnery
docker-compose down

# Zastavit a smazat data databaze
docker-compose down -v
```

---

## Troubleshooting

### WSDL se nenacita
1. Over, ze sluzba bezi: `docker-compose ps`
2. Zkontroluj logy: `docker-compose logs soap_app`
3. Zkus v prohlizeci: http://localhost:8000/?wsdl

### Chyba pripojeni k databazi
1. Pockej na plne spusteni PostgreSQL
2. Zkontroluj logy DB: `docker-compose logs db`
3. Restart: `docker-compose restart soap_app`

### Port 8000 je obsazeny
Zmen port v docker-compose.yml:
```yaml
ports:
  - "8080:8000"  # Zmena na 8080
```

---

## Struktura projektu

```
SOAP/
├── docker-compose.yml       # Docker orchestrace
├── Dockerfile               # Python kontejner
├── requirements.txt         # Python zavislosti
├── README.md                # Tento soubor
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── config.py            # Konfigurace
│   ├── models/
│   │   ├── database.py      # SQLAlchemy engine
│   │   └── book.py          # Book model
│   └── soap/
│       ├── types.py         # SOAP typy (Book, BookInput, BorrowResult)
│       ├── faults.py        # SOAP Faults
│       ├── service.py       # 8 SOAP operaci
│       └── application.py   # Spyne konfigurace
└── scripts/
    ├── init_db.sql          # Schema databaze
    └── seed_data.sql        # Ukazkova data
```
