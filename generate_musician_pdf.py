#!/usr/bin/env python3
"""
Generate a musician-friendly PDF guide for Frankenmusic
Using reportlab for professional PDF generation
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

# Define music-friendly colors
MUSIC_BLUE = HexColor("#1e3a8a")
STAFF_LINE = HexColor("#d4a574")
MUSIC_GREEN = HexColor("#059669")
ACCENT = HexColor("#dc2626")
LIGHT_BG = HexColor("#f0f4f8")

class MusicianPDFGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.pagesize = letter
        self.width, self.height = self.pagesize
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Create custom styles for musical document"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=36,
            textColor=MUSIC_BLUE,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=STAFF_LINE,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=MUSIC_GREEN,
            spaceAfter=10,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderPadding=6
        )
        
        self.section_style = ParagraphStyle(
            'SectionHead',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=MUSIC_BLUE,
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        )
        
        self.body_style = ParagraphStyle(
            'BodyText',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leading=14
        )
        
    def generate(self):
        """Generate the complete PDF"""
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=self.pagesize,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Title Page
        story.extend(self.create_title_page())
        story.append(PageBreak())
        
        # Table of Contents
        story.extend(self.create_toc())
        story.append(PageBreak())
        
        # Main Content
        story.extend(self.create_what_is_frankenmusic())
        story.append(PageBreak())
        
        story.extend(self.create_how_it_works())
        story.append(PageBreak())
        
        story.extend(self.create_melodic_rules())
        story.append(PageBreak())
        
        story.extend(self.create_harmonic_rules())
        story.append(PageBreak())
        
        story.extend(self.create_species_guide())
        story.append(PageBreak())
        
        story.extend(self.create_modes_guide())
        story.append(PageBreak())
        
        story.extend(self.create_getting_started())
        
        doc.build(story)
        print(f"✓ PDF generated: {self.filename}")
        
    def create_title_page(self):
        """Create the title page"""
        content = [
            Spacer(1, 1.5*inch),
            Paragraph("🎼 FRANKENMUSIC 🎼", self.title_style),
            Spacer(1, 0.2*inch),
            Paragraph("Renaissance Counterpoint Generator", self.subtitle_style),
            Spacer(1, 0.1*inch),
            Paragraph("A Musician's Guide", ParagraphStyle(
                'SmallSubtitle',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=STAFF_LINE,
                alignment=TA_CENTER,
                fontName='Helvetica-Oblique'
            )),
            Spacer(1, 2*inch),
            Paragraph(f"<i>Generated {datetime.now().strftime('%B %d, %Y')}</i>", ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=MUSIC_BLUE,
                alignment=TA_CENTER
            )),
        ]
        return content
        
    def create_toc(self):
        """Create Table of Contents"""
        content = [
            Paragraph("📑 Table of Contents", self.heading_style),
            Spacer(1, 0.2*inch),
        ]
        
        toc_items = [
            "1. What is Frankenmusic?",
            "2. How It Works: The Engine",
            "3. Melodic Rules (Cantus Firmus)",
            "4. Harmonic Rules (Counterpoint)",
            "5. Species of Counterpoint",
            "6. Church Modes",
            "7. Getting Started"
        ]
        
        for item in toc_items:
            content.append(Paragraph(f"• {item}", self.body_style))
            content.append(Spacer(1, 0.1*inch))
            
        return content
        
    def create_what_is_frankenmusic(self):
        """Main content: What is Frankenmusic"""
        content = [
            Paragraph("1. What is Frankenmusic?", self.heading_style),
            Spacer(1, 0.15*inch),
            
            Paragraph(
                "Frankenmusic is an <b>intelligent music composition engine</b> that generates counterpoint following the strict rules of Renaissance polyphony. Think of it as a tireless teacher who knows every rule of counterpoint by Knud Jeppesen and can generate valid voice combinations automatically.",
                self.body_style
            ),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>Core Capabilities:</b>", self.section_style),
            Spacer(1, 0.1*inch),
            
            Paragraph(
                "• Generate <b>Cantus Firmus</b> (CF) — the foundational melody<br/>"
                "• Create <b>Counterpoint voices</b> (CP) that respect the CF<br/>"
                "• Support <b>multiple church modes</b> (Dorian, Ionian, Phrygian, etc.)<br/>"
                "• Enforce ~20 compositional rules simultaneously<br/>"
                "• Export to <b>MIDI</b> for listening and further editing<br/>"
                "• Work with <b>multiple species</b> of counterpoint",
                self.body_style
            ),
            Spacer(1, 0.2*inch),
            
            Paragraph("<b>Perfect for:</b>", self.section_style),
            Spacer(1, 0.1*inch),
            
            Paragraph(
                "• Students learning counterpoint rules<br/>"
                "• Composers sketching polyphonic ideas<br/>"
                "• Music theorists exploring rule interactions<br/>"
                "• Musicologists studying Renaissance style<br/>"
                "• Anyone wanting to understand vocal counterpoint",
                self.body_style
            ),
        ]
        return content
        
    def create_how_it_works(self):
        """Explain the algorithm"""
        content = [
            Paragraph("2. How It Works: The Engine", self.heading_style),
            Spacer(1, 0.15*inch),
            
            Paragraph(
                "Frankenmusic uses a <b>tree-search algorithm</b> that builds melodies note-by-note, checking against all rules before adding each new note.",
                self.body_style
            ),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>The Search Process:</b>", self.section_style),
            Spacer(1, 0.1*inch),
            
            Paragraph(
                "<b>1. Start:</b> Choose a note to begin (usually the tonic)<br/>"
                "<b>2. Expand:</b> Try all valid next notes from your vocal range<br/>"
                "<b>3. Validate:</b> Check each candidate against 20 rules<br/>"
                "<b>4. Continue:</b> For valid notes, continue recursively<br/>"
                "<b>5. Complete:</b> When you reach the final note, end the phrase<br/>"
                "<b>6. Filter:</b> Apply quality metrics to keep best results",
                self.body_style
            ),
            Spacer(1, 0.2*inch),
            
            Paragraph("<b>Quality Filters:</b>", self.section_style),
            Spacer(1, 0.1*inch),
            
            Paragraph(
                "After generating complete melodies, Frankenmusic ranks results by:<br/>"
                "• <b>Variety:</b> Number of different pitches used<br/>"
                "• <b>Shape:</b> Where the highest note appears (climax position)<br/>"
                "• <b>Smoothness:</b> Limiting large jumps (discontinuity count)<br/>"
                "• <b>Tonal center:</b> How often the mode note appears",
                self.body_style
            ),
        ]
        return content
        
    def create_melodic_rules(self):
        """Melodic rules section"""
        content = [
            Paragraph("3. Melodic Rules (Cantus Firmus)", self.heading_style),
            Spacer(1, 0.15*inch),
            
            Paragraph(
                "These rules apply to the basic melody (Cantus Firmus). Every generated melody follows all of these:",
                self.body_style
            ),
            Spacer(1, 0.2*inch),
            
            Paragraph("<b>Range & Boundaries:</b>", self.section_style),
            Paragraph("• Starts on the <b>tonic (tonal center)</b><br/>"
                     "• Ends on the <b>tonic</b><br/>"
                     "• Penultimate note is the <b>2nd scale degree</b><br/>"
                     "• Stays within the vocal range specified",
                     self.body_style),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>Intervals (Jumps) Prohibited:</b>", self.section_style),
            Paragraph("• <b>Major 7th</b> (11 semitones)<br/>"
                     "• <b>Minor 7th</b> (10 semitones)<br/>"
                     "• <b>Tritone</b> (6 semitones)<br/>"
                     "• <b>Any interval larger than octave</b> (>12 semitones)<br/>"
                     "• <b>Minor 6th ascending</b> (allowed only descending)",
                     self.body_style),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>Tritone (Diabolus in Musica):</b>", self.section_style),
            Paragraph("• Can't appear between adjacent notes<br/>"
                     "• Can't appear between the highest/lowest in a phrase<br/>"
                     "• Can't appear in certain harmonic contexts",
                     self.body_style),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>Motion & Direction:</b>", self.section_style),
            Paragraph("• After a large jump (>2nd), the next note must move in <b>contrary direction</b><br/>"
                     "• This prevents awkward leaps in the wrong direction",
                     self.body_style),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>Note Repetition:</b>", self.section_style),
            Paragraph("• The same note cannot repeat consecutively<br/>"
                     "• Never more than 3 identical notes in a row (anywhere)<br/>"
                     "• No repeated melodic patterns within the phrase",
                     self.body_style),
        ]
        return content
        
    def create_harmonic_rules(self):
        """Harmonic rules section"""
        content = [
            Paragraph("4. Harmonic Rules (Counterpoint)", self.heading_style),
            Spacer(1, 0.15*inch),
            
            Paragraph(
                "When combining voices, additional harmonic rules ensure musical coherence:",
                self.body_style
            ),
            Spacer(1, 0.2*inch),
            
            Paragraph("<b>Parallel Motion (Forbidden):</b>", self.section_style),
            Paragraph("• <b>Direct 5ths:</b> Two voices can't both move to a perfect 5th interval<br/>"
                     "• <b>Direct 8ves:</b> Two voices can't both move to a perfect octave<br/>"
                     "<i>Exception: Allowed in lowest voices when not \"exposed\"</i>",
                     self.body_style),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>Consonance Requirements:</b>", self.section_style),
            Paragraph("• Most intervals between voices must be consonant (thirds, sixths, octaves, unisons)<br/>"
                     "• Perfect intervals (unison, 4th, 5th, octave) require special care<br/>"
                     "• Dissonances only allowed in specific contexts (passing tones, suspensions)",
                     self.body_style),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>Cadence Requirements:</b>", self.section_style),
            Paragraph("• At phrase end, the <b>highest voice (soprano)</b> must approach the final note by <b>step</b><br/>"
                     "• Usually: 2nd scale degree → tonic (rising step)<br/>"
                     "• This creates the characteristic Renaissance \"authentic cadence\" feel",
                     self.body_style),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>Repetition:</b>", self.section_style),
            Paragraph("• Can't have the same harmonic interval repeated more than 4 steps in a row<br/>"
                     "• Creates melodic variety in the counterpoint",
                     self.body_style),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>Unison Prohibition:</b>", self.section_style),
            Paragraph("• In 2-voice writing, unison is generally avoided<br/>"
                     "• Sometimes allowed at start/end for stylistic reasons",
                     self.body_style),
        ]
        return content
        
    def create_species_guide(self):
        """Species of counterpoint guide"""
        content = [
            Paragraph("5. Species of Counterpoint", self.heading_style),
            Spacer(1, 0.15*inch),
            
            Paragraph(
                "Frankenmusic supports multiple species, each with different rhythmic complexity:",
                self.body_style
            ),
            Spacer(1, 0.2*inch),
            
            Paragraph("<b>1st Species (Nota contra Nota)</b> ✓ <i>Fully Implemented</i>", self.section_style),
            Paragraph(
                "• <b>Rhythm:</b> Note-for-note with Cantus Firmus<br/>"
                "• <b>Interval:</b> Every beat is a consonant interval<br/>"
                "• <b>Character:</b> Pure, clean, pedagogical<br/>"
                "• Perfect for learning the basics",
                self.body_style
            ),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>2nd & 3rd Species</b> ⏳ <i>Partial</i>", self.section_style),
            Paragraph(
                "• <b>2nd Species:</b> 2 notes in CP for each CF note<br/>"
                "• <b>3rd Species:</b> 4 notes in CP for each CF note<br/>"
                "• <b>Challenge:</b> Passing tones, dissonance resolution<br/>"
                "• <i>Currently: Structure exists, dissonance rules incomplete</i>",
                self.body_style
            ),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>4th Species (Suspensions)</b> ⏳ <i>Not Yet</i>", self.section_style),
            Paragraph(
                "• <b>Rhythm:</b> Syncopated (tied notes crossing beats)<br/>"
                "• <b>Key Feature:</b> Suspensions (7-6, 4-3, 2-1)<br/>"
                "• <b>Dissonance:</b> Carefully prepared and resolved",
                self.body_style
            ),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>5th Species (Florid)</b> ⏳ <i>Not Yet</i>", self.section_style),
            Paragraph(
                "• <b>Rhythm:</b> Mixed durations combining all species<br/>"
                "• <b>Spirit:</b> Free, ornamental, fully composed<br/>"
                "• Most expressive but most challenging",
                self.body_style
            ),
        ]
        return content
        
    def create_modes_guide(self):
        """Church modes guide"""
        modes_data = [
            ["Mode", "Final", "Character", "Scale"],
            ["Ionian", "C", "Bright, major", "C D E F G A B C"],
            ["Dorian", "D", "Minor with raised 6th", "D E F G A B C D"],
            ["Phrygian", "E", "Minor, exotic", "E F G A B C D E"],
            ["Lydian", "F", "Major with raised 4th", "F G A B C D E F"],
            ["Mixolydian", "G", "Major with lowered 7th", "G A B C D E F G"],
            ["Aeolian", "A", "Natural minor", "A B C D E F G A"],
            ["Locrian", "B", "Minor with lowered 2nd", "B C D E F G A B"],
        ]
        
        content = [
            Paragraph("6. Church Modes", self.heading_style),
            Spacer(1, 0.15*inch),
            
            Paragraph(
                "Frankenmusic can generate music in any of the 8 church modes (also called ecclesiastical or medieval modes):",
                self.body_style
            ),
            Spacer(1, 0.2*inch),
            
            Table(modes_data, colWidths=[1.2*inch, 0.8*inch, 1.8*inch, 1.8*inch]),
            Spacer(1, 0.2*inch),
            
            Spacer(1, 0.15*inch),
            Paragraph(
                "<b>Pro Tip:</b> Each mode has a different feel. Dorian and Aeolian sound minor; Ionian, Lydian, and Mixolydian sound major; Phrygian and Locrian sound exotic or unsettling.",
                self.body_style
            ),
        ]
        
        # Apply table style
        if len(content) > 4:  # The table is at index 4
            table = content[4]
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), MUSIC_BLUE),
                ('TEXTCOLOR', (0,0), (-1,0), white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('BACKGROUND', (0,1), (-1,-1), LIGHT_BG),
                ('GRID', (0,0), (-1,-1), 0.5, black),
                ('FONTSIZE', (0,1), (-1,-1), 9),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, LIGHT_BG]),
            ]))
            
        return content
        
    def create_getting_started(self):
        """Getting started section"""
        content = [
            Paragraph("7. Getting Started", self.heading_style),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>Installation:</b>", self.section_style),
            Paragraph(
                "<font face='Courier'>$ git clone &lt;repo&gt;<br/>"
                "$ cd Frankenmusic<br/>"
                "$ python3 tests/test.py  <i># Run tests</i></font>",
                ParagraphStyle('Code', parent=self.styles['Normal'], fontSize=9, 
                             fontName='Courier', textColor=MUSIC_BLUE, spaceAfter=10)
            ),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>Simple Example (Python):</b>", self.section_style),
            Paragraph(
                "<font face='Courier' size='8'>"
                "from treeSearch import Voice<br/>"
                "from src.Note import ScaleMode<br/><br/>"
                "v = Voice(mode=ScaleMode.Dorian, length=8)<br/>"
                "v.search()  <i># Generate melodies</i><br/>"
                "for seq in v.pool:<br/>"
                "&nbsp;&nbsp;&nbsp;&nbsp;print(seq)  <i># Print notes</i>"
                "</font>",
                ParagraphStyle('Code', parent=self.styles['Normal'], fontSize=8, 
                             fontName='Courier', textColor=MUSIC_BLUE, spaceAfter=10)
            ),
            Spacer(1, 0.15*inch),
            
            Paragraph("<b>Output:</b>", self.section_style),
            Paragraph(
                "Generated melodies are stored as MIDI files in <b>output/midis/</b> and can be imported into any DAW (Ableton, Logic, Finale, Sibelius).",
                self.body_style
            ),
            Spacer(1, 0.2*inch),
            
            Paragraph("<b>Learn More:</b>", self.section_style),
            Paragraph(
                "See the docs/ folder (especially <b>backlog_reglas.md</b>) for detailed rule comparisons with Jeppesen's theoretical writings.<br/><br/>"
                "Jeppesen's <i>\"Counterpoint: A Comprehensive Study\"</i> remains the authoritative reference.",
                self.body_style
            ),
            Spacer(1, 0.3*inch),
            
            Paragraph(
                "<i>Frankenmusic brings Renaissance counterpoint into the digital age.</i>",
                ParagraphStyle('Tagline', parent=self.styles['Normal'], fontSize=11,
                             textColor=MUSIC_GREEN, alignment=TA_CENTER,
                             fontName='Helvetica-Oblique', spaceAfter=10)
            ),
        ]
        return content


if __name__ == "__main__":
    generator = MusicianPDFGenerator("output/Frankenmusic_Musicians_Guide.pdf")
    generator.generate()
