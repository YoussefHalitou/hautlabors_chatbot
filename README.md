# Haut Labor Oldenburg - AI Assistant

Ein KI-Assistent für die Praxis Hautlabor von Dr. med. Lara Pfahl in Oldenburg. Der Assistent bietet detaillierte Informationen über ästhetische Behandlungen und hilft Patienten bei der Terminbuchung.

## 🚀 Features

- **Umfassende Behandlungsinformationen**: Über 30 verschiedene ästhetische Behandlungen
- **JSON Knowledge Base**: Lokale Wissensdatenbank mit strukturierten Behandlungsdaten
- **Intelligente Suche**: Effiziente Keyword-basierte Suche durch Behandlungen und Verfahren
- **Web-Interface**: Moderne Chat-Widget Integration für Websites
- **CLI-Interface**: Kommandozeilen-Chat für Tests und Entwicklung
- **Mehrsprachige Unterstützung**: Primär auf Deutsch mit formeller "Sie"-Anrede

## 🏗️ Architektur

### Knowledge Base System
Das System verwendet eine lokale JSON-Datei (`combined_database_newest.json`) als Wissensdatenbank:

```
{
  "treatments": [
    {
      "id": "treatment-id",
      "treatment_name": "Behandlungsname",
      "category": "Gesicht|Körper|Männer",
      "tags": ["tag1", "tag2"],
      "content": {
        "description": "Beschreibung",
        "mechanism": "Funktionsweise",
        "details": {...},
        "faqs": [...]
      }
    }
  ],
  "pages": [...] // Zusätzliche Seiteninformationen
}
```

### AI Agent System
- **PydanticAI Framework**: Modernes Python-Framework für AI-Agenten
- **OpenAI Integration**: GPT-4o-mini für natürliche Sprachverarbeitung
- **Tool System**: Spezialisierte Tools für Wissenssuche und Behandlungsdetails

## 📦 Installation & Setup

### 1. Repository klonen
```bash
git clone <repository-url>
cd clinic_ai_agent
```

### 2. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 3. Umgebungsvariablen konfigurieren
Erstellen Sie eine `.env` Datei:
```env
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o-mini
```

### 4. Knowledge Base vorbereiten
Stellen Sie sicher, dass `combined_database_newest.json` im Hauptverzeichnis liegt.

## 🚀 Verwendung

### Web-Interface starten
```bash
python app.py
```
Das Web-Interface ist dann unter `http://localhost:8080` verfügbar.

### CLI-Chat verwenden
```bash
python clinic_chat.py
```

### Knowledge Base testen
```bash
python test_json_kb.py
```

## 🔧 Entwicklung

### Neue Behandlungen hinzufügen
1. Öffnen Sie `combined_database_newest.json`
2. Fügen Sie einen neuen Behandlungseintrag im `treatments` Array hinzu
3. Stellen Sie sicher, dass alle erforderlichen Felder ausgefüllt sind

### System anpassen
- **Search Logic**: Bearbeiten Sie die Suchfunktionen in `pydantic_ai_expert.py`
- **System Prompt**: Anpassungen in `system_prompt.txt`
- **Web Interface**: HTML/CSS/JS in `templates/index.html`

## 📊 Knowledge Base Statistiken

Die aktuelle Wissensdatenbank enthält:
- **30 Behandlungen** in 3 Hauptkategorien:
  - Gesicht (15 Behandlungen)
  - Körper (6 Behandlungen)  
  - Männer (7 Behandlungen)
  - Weitere spezialisierte Behandlungen

- **Behandlungsarten**:
  - Laser-Behandlungen (CO₂, LaseMD, Lumecca)
  - Injektionsbehandlungen (Botox, Filler, Radiesse, Sculptra)
  - Hautverbesserung (HydraFacial, Microneedling, PRP)
  - Körperformung (Morpheus8, Lipolyse)
  - Spezialbehandlungen für Männer

## 🛠️ Tools & Funktionen

Der AI-Agent verfügt über spezialisierte Tools:

- `search_knowledge_base()`: Durchsucht die Wissensdatenbank nach relevanten Informationen
- `get_treatment_details()`: Liefert detaillierte Informationen zu spezifischen Behandlungen
- `list_treatments_by_category()`: Listet Behandlungen nach Kategorien auf

## 📱 Deployment

### Lokale Entwicklung
```bash
python app.py
```

### Produktion (Render.com/Heroku)
Das System ist bereit für Deployment auf Cloud-Plattformen:
- `Procfile` für Heroku
- `render.yaml` für Render.com
- Health-Check Endpoint: `/health`

## 🔒 Sicherheit & Datenschutz

- Keine persönlichen Daten werden gespeichert
- Conversation History nur in-memory (Session-basiert)
- Sichere OpenAI API Integration
- Keine Diagnosen oder medizinische Beratung

## 🤝 Beitragen

1. Fork des Repositories
2. Feature Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen

## 📄 Lizenz

Dieses Projekt ist lizenziert unter der MIT License - siehe die [LICENSE](LICENSE) Datei für Details.

## 📞 Kontakt

**Hautlabor Dr. med. Lara Pfahl**
- Website: https://haut-labor.de
- Terminbuchung: [Online buchen](https://haut-labor.de/termin-vereinbaren/#termin)

---

*Powered by PydanticAI, OpenAI GPT-4o-mini, and modern web technologies*
