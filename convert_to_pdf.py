"""
Convert Research_Paper.md to IEEE Conference Paper format PDF using fpdf2.
Matches the formatting style of IEEE NIGERCON / standard IEEE conference papers:
  - Two-column layout
  - Times/serif font
  - Roman numeral section headings (centered, ALL CAPS)
  - Italic subsection headings (A., B., C.)
  - Bold italic abstract with em-dash prefix
  - Compact references in 8pt
"""

import os
import re
from fpdf import FPDF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(SCRIPT_DIR, "Research_Paper.md")
PDF_PATH = os.path.join(SCRIPT_DIR, "Research_Paper.pdf")
IMAGES_DIR = os.path.join(SCRIPT_DIR, "sample_images")

# IEEE standard page dimensions (US Letter)
PAGE_W = 215.9  # mm
PAGE_H = 279.4  # mm
MARGIN_TOP = 19.0
MARGIN_BOTTOM = 25.4
MARGIN_LEFT = 17.0  # ~0.67in
MARGIN_RIGHT = 17.0
COL_GAP = 5.0  # gap between columns in mm

# Roman numeral conversion
def to_roman(n):
    vals = [(1000,'M'),(900,'CM'),(500,'D'),(400,'CD'),
            (100,'C'),(90,'XC'),(50,'L'),(40,'XL'),
            (10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]
    result = ''
    for v, r in vals:
        while n >= v:
            result += r
            n -= v
    return result


def clean(text):
    """Remove markdown bold/italic markers for clean PDF text."""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = text.replace('\u2014', '--').replace('\u2013', '-')
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u2192', '->').replace('\u00d7', 'x')
    text = text.replace('\u2194', '<->').replace('\u2265', '>=')
    text = text.replace('\u03c3\u00b2', 'sigma^2').replace('\u03bc', 'mu')
    text = text.replace('\u03b5', 'epsilon').replace('\u03b3', 'gamma')
    text = text.replace('\u03b2', 'beta').replace('\u03a3', 'Sum')
    text = text.replace('\u015f', 's').replace('\u2022', '-')
    text = text.encode('latin-1', errors='replace').decode('latin-1')
    return text.strip()


class IEEEPaperPDF(FPDF):
    """
    Custom PDF class implementing IEEE two-column conference paper format.
    """

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='letter')
        self.set_margins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT)
        self.set_auto_page_break(auto=True, margin=MARGIN_BOTTOM)
        self.alias_nb_pages()
        self._col = 0  # 0 = left, 1 = right
        self._in_two_col = False
        self._col_y_start = MARGIN_TOP
        self._saved_y = MARGIN_TOP
        self._table_counter = 0
        self._fig_counter = 0

    @property
    def col_width(self):
        """Width of a single column."""
        usable = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
        return (usable - COL_GAP) / 2.0

    @property
    def col_x(self):
        """X position of current column."""
        if self._col == 0:
            return MARGIN_LEFT
        else:
            return MARGIN_LEFT + self.col_width + COL_GAP

    def header(self):
        """IEEE-style page header with conference name."""
        self.set_font("Times", "BI", 8)
        self.set_text_color(0, 0, 0)
        self.set_xy(MARGIN_LEFT, 8)
        self.cell(PAGE_W - MARGIN_LEFT - MARGIN_RIGHT, 4,
                  "2026 COER University -- Department of Computer Science", align="L")
        self.ln(2)

    def footer(self):
        """IEEE-style page footer (no visible page number in some IEEE, but we add one)."""
        pass  # IEEE conference papers typically don't have page numbers from authors

    # ── Column management ──

    def start_two_col(self):
        """Begin two-column mode."""
        self._in_two_col = True
        self._col = 0
        self._col_y_start = self.get_y()
        self.set_left_margin(self.col_x)
        self.set_right_margin(PAGE_W - self.col_x - self.col_width)
        self.set_x(self.col_x)

    def next_column(self):
        """Move to the next column or next page."""
        if self._col == 0:
            self._saved_y = self.get_y()
            self._col = 1
            self.set_left_margin(self.col_x)
            self.set_right_margin(PAGE_W - self.col_x - self.col_width)
            self.set_xy(self.col_x, self._col_y_start)
        else:
            self._col = 0
            self.add_page()
            self._col_y_start = self.get_y()
            self.set_left_margin(self.col_x)
            self.set_right_margin(PAGE_W - self.col_x - self.col_width)
            self.set_x(self.col_x)

    def _check_col_break(self, h=10):
        """Check if we need to break to next column/page."""
        if self._in_two_col:
            if self.get_y() + h > PAGE_H - MARGIN_BOTTOM:
                self.next_column()

    def accept_page_break(self):
        """Override to handle two-column page breaks."""
        if self._in_two_col:
            if self._col == 0:
                self._saved_y = max(self._saved_y, self.get_y()) if hasattr(self, '_saved_y') else self.get_y()
                self._col = 1
                self.set_left_margin(self.col_x)
                self.set_right_margin(PAGE_W - self.col_x - self.col_width)
                self.set_xy(self.col_x, self._col_y_start)
                return False
            else:
                self._col = 0
                self._col_y_start = MARGIN_TOP + 6  # after header
                self.set_left_margin(self.col_x)
                self.set_right_margin(PAGE_W - self.col_x - self.col_width)
                return True
        return True

    def _set_col_margins(self):
        """Set margins for current column."""
        if self._in_two_col:
            self.set_left_margin(self.col_x)
            self.set_right_margin(PAGE_W - self.col_x - self.col_width)
            self.set_x(self.col_x)

    def _restore_full_width(self):
        """Temporarily use full page width."""
        self.set_left_margin(MARGIN_LEFT)
        self.set_right_margin(MARGIN_RIGHT)
        self.set_x(MARGIN_LEFT)

    def _restore_col_width(self):
        """Restore column-width margins."""
        self._set_col_margins()

    # ── Title and author block (full-width) ──

    def add_title(self, title):
        """IEEE centered title in ~24pt Times."""
        self._restore_full_width()
        self.set_font("Times", "", 24)
        self.set_text_color(0, 0, 0)
        self.ln(4)
        self.multi_cell(0, 10, title, align="C")
        self.ln(4)

    def add_authors(self, authors):
        """
        Add author block. `authors` is a list of dicts:
        [{"name": ..., "dept": ..., "univ": ..., "city": ..., "email": ...}, ...]
        """
        self._restore_full_width()
        usable = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
        col_w = usable / len(authors)

        x_start = MARGIN_LEFT
        y_start = self.get_y()

        for author in authors:
            self.set_xy(x_start, y_start)

            # Name
            self.set_font("Times", "", 11)
            self.set_text_color(0, 0, 0)
            self.cell(col_w, 5, author["name"], align="C",
                      new_x="LMARGIN", new_y="NEXT")

            self.set_x(x_start)
            self.set_font("Times", "I", 10)
            self.cell(col_w, 5, author.get("dept", ""), align="C",
                      new_x="LMARGIN", new_y="NEXT")

            self.set_x(x_start)
            self.set_font("Times", "", 10)
            self.cell(col_w, 5, author.get("univ", ""), align="C",
                      new_x="LMARGIN", new_y="NEXT")

            self.set_x(x_start)
            self.cell(col_w, 5, author.get("city", ""), align="C",
                      new_x="LMARGIN", new_y="NEXT")

            self.set_x(x_start)
            self.set_font("Times", "I", 10)
            self.cell(col_w, 5, author.get("email", ""), align="C",
                      new_x="LMARGIN", new_y="NEXT")

            x_start += col_w

        self.set_y(self.get_y() + 6)

    # ── Abstract (full-width, then switch to two-col) ──

    def add_abstract(self, text, keywords=None):
        """IEEE abstract: Bold italic prefix, bold body text."""
        self._restore_full_width()
        self.set_font("Times", "BI", 9)
        self.set_text_color(0, 0, 0)
        # Abstract em-dash prefix
        abstract_prefix = "Abstract--"
        w_prefix = self.get_string_width(abstract_prefix) + 1
        x = MARGIN_LEFT
        y = self.get_y()
        self.set_xy(x, y)
        self.cell(w_prefix, 4.5, abstract_prefix)

        # Body in bold 9pt
        self.set_font("Times", "B", 9)
        # Multi-cell for rest
        self.multi_cell(0, 4.5, text)
        self.ln(2)

        if keywords:
            self.set_font("Times", "BI", 9)
            k_prefix = "Keywords--"
            self.cell(self.get_string_width(k_prefix) + 1, 4.5, k_prefix)
            self.set_font("Times", "B", 9)
            self.multi_cell(0, 4.5, keywords)
            self.ln(3)

    # ── Section headings ──

    def section_heading(self, num, title):
        """
        IEEE major section heading: centered, Roman numeral, ALL CAPS.
        Example: "I. INTRODUCTION"
        """
        self._check_col_break(12)
        self._set_col_margins()
        self.ln(3)
        self.set_font("Times", "", 10)
        self.set_text_color(0, 0, 0)
        roman = to_roman(num)
        heading_text = f"{roman}. {title.upper()}"
        self.cell(self.col_width if self._in_two_col else 0, 5,
                  heading_text, align="C", new_x="LMARGIN", new_y="NEXT")
        self._set_col_margins()
        self.ln(2)

    def subsection_heading(self, letter, title):
        """
        IEEE subsection heading: Italic, left-aligned.
        Example: "A. Background"
        """
        self._check_col_break(10)
        self._set_col_margins()
        self.ln(2)
        self.set_font("Times", "I", 10)
        self.set_text_color(0, 0, 0)
        heading_text = f"{letter}. {title}"
        self.cell(0, 5, heading_text, new_x="LMARGIN", new_y="NEXT")
        self._set_col_margins()
        self.ln(1)

    def subsubsection_heading(self, title):
        """IEEE subsubsection: Italic, indented."""
        self._check_col_break(8)
        self._set_col_margins()
        self.ln(1)
        self.set_font("Times", "I", 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, title, new_x="LMARGIN", new_y="NEXT")
        self._set_col_margins()
        self.ln(1)

    # ── Body text ──

    def body_text(self, text):
        """10pt Times Roman, justified body text."""
        self._check_col_break(6)
        self._set_col_margins()
        self.set_font("Times", "", 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 4.5, text, align="J")
        self.ln(1.5)

    def bullet_item(self, text):
        """Bullet point item."""
        self._check_col_break(6)
        self._set_col_margins()
        self.set_font("Times", "", 10)
        self.set_text_color(0, 0, 0)
        x = self.get_x()
        indent = 4
        self.cell(indent, 4.5, chr(149))  # bullet char
        self.multi_cell(0, 4.5, text, align="J")
        self.ln(1)

    def numbered_item(self, num, text):
        """Numbered list item."""
        self._check_col_break(6)
        self._set_col_margins()
        self.set_font("Times", "", 10)
        self.set_text_color(0, 0, 0)
        indent = 6
        self.cell(indent, 4.5, f"{num})")
        self.multi_cell(0, 4.5, text, align="J")
        self.ln(1)

    def code_block(self, text):
        """Code block in monospace."""
        self._check_col_break(10)
        self._set_col_margins()
        self.set_font("Courier", "", 7)
        self.set_text_color(0, 0, 0)
        lines = text.strip().split("\n")
        for line in lines:
            self.cell(0, 3.5, "  " + line, new_x="LMARGIN", new_y="NEXT")
            self._set_col_margins()
        self.ln(2)

    # ── Tables (IEEE style) ──

    def add_table(self, caption, headers, rows, col_widths=None):
        """
        IEEE-style table with caption above.
        Caption format: "TABLE I" in small caps + newline + description
        """
        self._table_counter += 1
        roman = to_roman(self._table_counter)

        # Calculate total width
        if col_widths is None:
            total_w = self.col_width if self._in_two_col else (PAGE_W - MARGIN_LEFT - MARGIN_RIGHT)
            col_widths = [total_w / len(headers)] * len(headers)

        total_w = sum(col_widths)
        needed = 8 + len(rows) * 5 + 8
        self._check_col_break(needed)
        self._set_col_margins()

        # Caption above table
        self.ln(2)
        self.set_font("Times", "", 8)
        self.set_text_color(0, 0, 0)
        # "TABLE I" line
        table_label = f"TABLE {roman}"
        self.cell(0, 4, table_label, align="C", new_x="LMARGIN", new_y="NEXT")
        self._set_col_margins()
        # Description
        self.set_font("Times", "", 8)
        self.multi_cell(0, 3.5, caption, align="C")
        self._set_col_margins()
        self.ln(1)

        # Calculate starting x to center table
        current_col_w = self.col_width if self._in_two_col else (PAGE_W - MARGIN_LEFT - MARGIN_RIGHT)
        table_x = self.get_x() + (current_col_w - total_w) / 2.0
        if table_x < self.get_x():
            table_x = self.get_x()

        # Header row
        self.set_font("Times", "B", 8)
        self.set_text_color(0, 0, 0)
        y_before = self.get_y()
        for i, h in enumerate(headers):
            x = table_x + sum(col_widths[:i])
            self.set_xy(x, y_before)
            self.cell(col_widths[i], 4.5, h, border="TB", align="C")
        self.set_y(y_before + 4.5)
        self._set_col_margins()

        # Data rows
        self.set_font("Times", "", 8)
        for row in rows:
            y_row = self.get_y()
            max_h = 4.5
            for i, cell_text in enumerate(row):
                x = table_x + sum(col_widths[:i])
                self.set_xy(x, y_row)
                # Check if text will wrap
                tw = self.get_string_width(cell_text)
                if tw > col_widths[i] - 2:
                    # Multi-line cell
                    self.multi_cell(col_widths[i], 3.5, cell_text, border=0, align="C")
                    cell_h = self.get_y() - y_row
                    max_h = max(max_h, cell_h)
                else:
                    align = "L" if i == 0 else "C"
                    self.cell(col_widths[i], 4.5, cell_text, border=0, align=align)
            self.set_y(y_row + max_h)
            self._set_col_margins()

        # Bottom border
        y_end = self.get_y()
        self.line(table_x, y_end, table_x + total_w, y_end)
        self.ln(3)

    # ── Figures ──

    def add_figure(self, path, caption, width=None):
        """Add a figure with IEEE-style caption below."""
        self._fig_counter += 1
        if not os.path.exists(path):
            self.body_text(f"[Image not found: {os.path.basename(path)}]")
            return

        if width is None:
            width = self.col_width if self._in_two_col else (PAGE_W - MARGIN_LEFT - MARGIN_RIGHT) * 0.7

        self._check_col_break(50)
        self._set_col_margins()

        # Center in column
        col_w = self.col_width if self._in_two_col else (PAGE_W - MARGIN_LEFT - MARGIN_RIGHT)
        x = self.get_x() + (col_w - width) / 2.0
        self.image(path, x=x, w=width)
        self.ln(1)

        # Caption
        self._set_col_margins()
        self.set_font("Times", "", 8)
        self.set_text_color(0, 0, 0)
        caption_text = f"Fig. {self._fig_counter}. {caption}"
        self.multi_cell(0, 3.5, caption_text, align="C")
        self.ln(2)

    # ── References ──

    def add_references(self, refs):
        """IEEE reference list in 8pt."""
        self._set_col_margins()
        self.ln(2)
        # Section heading for references (no number)
        self.set_font("Times", "", 10)
        self.set_text_color(0, 0, 0)
        w = self.col_width if self._in_two_col else 0
        self.cell(w, 5, "REFERENCES", align="C", new_x="LMARGIN", new_y="NEXT")
        self._set_col_margins()
        self.ln(2)

        self.set_font("Times", "", 8)
        for ref in refs:
            self._check_col_break(8)
            self._set_col_margins()
            self.multi_cell(0, 3.5, clean(ref), align="J")
            self.ln(1)


def build_pdf():
    """Build the IEEE-formatted research paper PDF."""
    print("[INFO] Building IEEE-format PDF ...")

    pdf = IEEEPaperPDF()
    pdf.add_page()

    # ═══════════════════════════════════════════════════════════════
    # TITLE (full width, centered)
    # ═══════════════════════════════════════════════════════════════
    pdf.add_title(
        "Handwritten Digit Recognition Using\n"
        "Convolutional Neural Networks:\n"
        "A Deep Learning Approach"
    )

    # ═══════════════════════════════════════════════════════════════
    # AUTHORS (full width, centered)
    # ═══════════════════════════════════════════════════════════════
    pdf.add_authors([{
        "name": "Abhay Singh",
        "dept": "Department of Computer Science",
        "univ": "COER University",
        "city": "Roorkee, India",
        "email": "abhaychauhan5051a@gmail.com",
    }])

    # ═══════════════════════════════════════════════════════════════
    # ABSTRACT (full width)
    # ═══════════════════════════════════════════════════════════════
    pdf.add_abstract(
        clean(
            "Handwritten digit recognition is a fundamental problem in pattern recognition and computer "
            "vision with widespread applications in postal mail sorting, bank cheque processing, and "
            "document digitisation. This paper presents a Convolutional Neural Network (CNN) based approach "
            "for recognising handwritten digits (0-9) using the MNIST benchmark dataset. The proposed model "
            "architecture employs two convolutional layers with ReLU activation, max-pooling for spatial "
            "downsampling, batch normalisation for training stability, and dropout regularisation to prevent "
            "overfitting. The model was implemented using TensorFlow/Keras and trained on 60,000 labelled "
            "images, achieving a test accuracy of 98.91% on the 10,000-image test set. We further demonstrate "
            "a real-time deployment through a Streamlit-based web application featuring an interactive drawing "
            "canvas. This paper provides a comprehensive analysis of the CNN architecture, training dynamics, "
            "performance evaluation, and potential enhancements for production deployment."
        ),
        keywords=clean(
            "Handwritten Digit Recognition, Convolutional Neural Network, Deep Learning, "
            "MNIST, Image Classification, TensorFlow, Pattern Recognition"
        ),
    )

    # ═══════════════════════════════════════════════════════════════
    # BEGIN TWO-COLUMN LAYOUT
    # ═══════════════════════════════════════════════════════════════
    pdf.start_two_col()

    # ── I. INTRODUCTION ──
    pdf.section_heading(1, "Introduction")

    pdf.subsection_heading("A", "Background")
    pdf.body_text(clean(
        "Handwritten digit recognition (HDR) is one of the most extensively studied problems in the "
        "field of computer vision and machine learning. The task involves classifying images of individual "
        "handwritten digits into one of ten classes (0 through 9). Despite its apparent simplicity, HDR "
        "poses significant challenges due to the inherent variability in human handwriting -- differences "
        "in stroke width, slant, size, and personal writing style create a vast space of possible "
        "representations for each digit [1]."
    ))
    pdf.body_text(clean(
        "The advancement of deep learning, particularly Convolutional Neural Networks (CNNs), has "
        "revolutionised the field of image recognition. CNNs have demonstrated remarkable capabilities "
        "in automatically learning hierarchical feature representations from raw pixel data, eliminating "
        "the need for manual feature engineering that characterised earlier approaches [2]."
    ))

    pdf.subsection_heading("B", "Problem Statement")
    pdf.body_text(clean(
        "Traditional machine learning approaches to handwritten digit recognition -- such as Support Vector "
        "Machines (SVMs) and k-Nearest Neighbours (k-NN) -- depend heavily on handcrafted features and "
        "often fail to capture the spatial relationships inherent in image data. When a 28x28 image is "
        "flattened into a 784-dimensional vector for a fully connected network, all spatial locality "
        "information is lost, leading to suboptimal classification performance and excessive parameter "
        "counts [3]."
    ))
    pdf.body_text(clean(
        "This paper addresses the problem by leveraging CNNs, which maintain spatial structure through "
        "local connectivity, shared weights, and hierarchical feature learning, resulting in significantly "
        "improved recognition accuracy with fewer trainable parameters."
    ))

    pdf.subsection_heading("C", "Objectives")
    pdf.body_text(clean(
        "The objectives of this research are:"
    ))
    objectives = [
        "To design and implement a CNN architecture optimised for handwritten digit classification on the MNIST dataset.",
        "To evaluate the model's performance in terms of accuracy, loss convergence, and generalisation capability.",
        "To analyse the role of each architectural component (convolution, pooling, dropout, batch normalisation).",
        "To deploy the trained model in a real-time web application for practical digit recognition.",
        "To propose improvements and discuss real-world applications.",
    ]
    for i, obj in enumerate(objectives, 1):
        pdf.numbered_item(i, clean(obj))

    pdf.subsection_heading("D", "Significance")
    pdf.body_text(clean(
        "Handwritten digit recognition serves as a gateway problem in deep learning education and has "
        "direct real-world impact in:"
    ))
    apps = [
        "Postal automation -- Automated ZIP code reading for mail sorting [4]",
        "Banking -- Cheque amount recognition and validation [5]",
        "Document digitisation -- Converting handwritten forms to machine-readable text [6]",
        "Mobile computing -- On-device handwriting input recognition [7]",
    ]
    for a in apps:
        pdf.bullet_item(clean(a))

    # ── II. LITERATURE REVIEW ──
    pdf.section_heading(2, "Literature Review")

    pdf.subsection_heading("A", "Classical Approaches")
    pdf.body_text(clean(
        "Early work on digit recognition relied on statistical pattern recognition methods. Vapnik and "
        "colleagues demonstrated the effectiveness of Support Vector Machines (SVMs) on the MNIST dataset, "
        "achieving error rates of approximately 1.4% [8]. k-Nearest Neighbours (k-NN) with various "
        "distance metrics achieved error rates around 3-5%, depending on the feature representation "
        "used [9]. Random Forests and Gradient Boosted Decision Trees were also applied, typically achieving "
        "accuracies between 96-97% on MNIST [10]."
    ))

    pdf.subsection_heading("B", "Neural Network Approaches")
    pdf.body_text(clean(
        "The resurgence of neural networks began with LeCun et al.'s seminal work on LeNet-5 (1998), "
        "a pioneering CNN architecture that achieved a 0.8% error rate on MNIST [11]. Multi-Layer "
        "Perceptrons (MLPs) without convolutional layers typically achieved error rates of 1.5-3%, "
        "demonstrating the clear advantage of convolutional architectures [12]."
    ))

    pdf.subsection_heading("C", "Modern Deep Learning Approaches")
    pdf.body_text(clean(
        "Modern architectures have pushed MNIST accuracy to near-perfect levels. Table I compares "
        "the key methods and their error rates."
    ))
    pdf.add_table(
        "COMPARISON OF METHODS ON THE MNIST TEST SET",
        ["Method", "Error (%)", "Year", "Ref."],
        [
            ["LeNet-5", "0.80", "1998", "[11]"],
            ["SVM (RBF)", "1.40", "1998", "[8]"],
            ["Deep CNN", "0.35", "2012", "[13]"],
            ["DropConnect", "0.21", "2013", "[14]"],
            ["Batch-Norm CNN", "0.29", "2015", "[15]"],
            ["Ensemble CNNs", "0.17", "2016", "[16]"],
            ["Capsule Net", "0.25", "2017", "[17]"],
        ],
        col_widths=[24, 14, 10, 8],
    )

    pdf.subsection_heading("D", "Research Gap")
    pdf.body_text(clean(
        "While several high-accuracy models exist, most research focuses solely on maximising accuracy "
        "without addressing practical deployment. This paper bridges that gap by (a) providing a "
        "well-documented, reproducible CNN implementation with detailed architectural analysis, and "
        "(b) demonstrating real-time deployment through a web-based interactive application."
    ))

    # ── III. DATASET DESCRIPTION ──
    pdf.section_heading(3, "Dataset Description")

    pdf.subsection_heading("A", "The MNIST Dataset")
    pdf.body_text(clean(
        "The Modified National Institute of Standards and Technology (MNIST) dataset [11] is the most "
        "widely used benchmark for handwritten digit recognition. It was created by re-sampling and "
        "normalising digits from the original NIST Special Databases 1 and 3."
    ))
    pdf.add_table(
        "MNIST DATASET PROPERTIES",
        ["Property", "Value"],
        [
            ["Total images", "70,000"],
            ["Training set", "60,000"],
            ["Test set", "10,000"],
            ["Image dimensions", "28 x 28 pixels"],
            ["Colour space", "Grayscale"],
            ["Pixel range", "0-255"],
            ["Classes", "10 (digits 0-9)"],
        ],
        col_widths=[28, 28],
    )

    pdf.subsection_heading("B", "Sample Visualisation")
    pdf.add_figure(
        os.path.join(IMAGES_DIR, "training_samples.png"),
        "Representative handwritten digits from the MNIST training set.",
        width=pdf.col_width * 0.95,
    )

    pdf.subsection_heading("C", "Data Characteristics")
    pdf.body_text(clean(
        "The MNIST dataset is approximately balanced across all 10 classes, with each digit represented "
        "by roughly 5,500-7,000 training samples. Images are centre-of-mass aligned and size-normalised "
        "to fit within a 20x20 pixel bounding box. Digits are anti-aliased, producing greyscale pixels "
        "at the edges of strokes."
    ))

    # ── IV. METHODOLOGY ──
    pdf.section_heading(4, "Methodology")

    pdf.subsection_heading("A", "Data Preprocessing")
    pdf.body_text(clean("Three preprocessing steps were applied:"))
    pdf.body_text(clean(
        "1) Reshaping: Images reshaped from (N, 28, 28) to (N, 28, 28, 1) to add the channel dimension "
        "required by CNNs. "
        "2) Normalisation: Pixel values scaled from [0, 255] to [0.0, 1.0] for faster convergence and "
        "numerical stability [18]. "
        "3) One-Hot Encoding: Integer labels converted to binary vectors of length 10 for categorical "
        "cross-entropy loss."
    ))

    pdf.subsection_heading("B", "Model Architecture")
    pdf.body_text(clean(
        "The proposed CNN architecture consists of a feature extraction block followed by a classification "
        "head. The architecture is defined as follows:"
    ))
    pdf.code_block(
        "Input: 28 x 28 x 1\n"
        "-- Feature Extraction --\n"
        "Conv2D(32, 3x3, ReLU)  -> 26x26x32\n"
        "Conv2D(64, 3x3, ReLU)  -> 24x24x64\n"
        "MaxPool2D(2x2)         -> 12x12x64\n"
        "Dropout(0.25)          -> 12x12x64\n"
        "-- Classification Head --\n"
        "Flatten()              -> 9,216\n"
        "Dense(128, ReLU)       -> 128\n"
        "BatchNorm()            -> 128\n"
        "Dropout(0.50)          -> 128\n"
        "Dense(10, Softmax)     -> 10"
    )
    pdf.body_text("Total parameters: ~1,199,882. Trainable: ~1,199,370.")

    pdf.subsection_heading("C", "Layer-by-Layer Justification")

    pdf.subsubsection_heading("1) Convolutional Layers:")
    pdf.body_text(clean(
        "The convolution operation applies learnable 3x3 filters across the input, producing feature maps. "
        "The first layer (32 filters) learns low-level features such as edges and corners. The second layer "
        "(64 filters) learns higher-level combinations -- curves, loops, and stroke patterns [19]."
    ))

    pdf.subsubsection_heading("2) ReLU Activation:")
    pdf.body_text(clean(
        "f(x) = max(0, x). Chosen over sigmoid/tanh for computational efficiency, sparse activation, "
        "and gradient flow in deep networks [20]."
    ))

    pdf.subsubsection_heading("3) Max Pooling:")
    pdf.body_text(clean(
        "MaxPooling2D with a 2x2 window performs spatial downsampling, halving both dimensions. This "
        "provides translation invariance and reduces computation by 75% [21]."
    ))

    pdf.subsubsection_heading("4) Dropout:")
    pdf.body_text(clean(
        "Dropout randomly zeroes activations during training. Two layers are used: 0.25 after pooling "
        "for mild regularisation, and 0.50 before output for aggressive regularisation. This implicitly "
        "creates an ensemble of 2^n sub-networks [22]."
    ))

    pdf.subsubsection_heading("5) Batch Normalisation:")
    pdf.body_text(clean(
        "Normalises layer inputs to zero mean and unit variance, enabling higher learning rates and "
        "reducing sensitivity to weight initialisation [15]."
    ))

    pdf.subsubsection_heading("6) Softmax Output:")
    pdf.body_text(clean(
        "Converts raw logits into a probability distribution over 10 classes, with all values summing "
        "to 1.0 for direct interpretation as class probabilities."
    ))

    pdf.subsection_heading("D", "Training Configuration")
    pdf.add_table(
        "TRAINING HYPERPARAMETERS",
        ["Parameter", "Value"],
        [
            ["Optimiser", "Adam [23]"],
            ["Learning rate", "0.001"],
            ["Loss", "Cat. cross-entropy"],
            ["Batch size", "128"],
            ["Max epochs", "15"],
            ["Val. split", "10%"],
            ["Early stopping", "patience=3"],
        ],
        col_widths=[24, 32],
    )

    # ── V. RESULTS AND ANALYSIS ──
    pdf.section_heading(5, "Results and Analysis")

    pdf.subsection_heading("A", "Training Performance")
    pdf.body_text(clean(
        "The model was trained for 9 epochs (early stopping triggered with patience=3, monitoring "
        "validation loss). Training accuracy reached 95.4% in the first epoch and improved monotonically "
        "to 99.3% by epoch 9. The gap between training and validation accuracy remained below 0.5%, "
        "confirming effective regularisation."
    ))
    pdf.add_figure(
        os.path.join(IMAGES_DIR, "training_curves.png"),
        "Training and validation accuracy (left) and loss (right) curves across 9 epochs.",
        width=pdf.col_width * 0.95,
    )

    pdf.subsection_heading("B", "Test Set Evaluation")
    pdf.add_table(
        "TEST SET EVALUATION RESULTS",
        ["Metric", "Value"],
        [
            ["Test accuracy", "98.91%"],
            ["Test loss", "0.0304"],
            ["Error rate", "1.09%"],
            ["Misclassified", "~109 / 10,000"],
        ],
        col_widths=[24, 32],
    )
    pdf.body_text(clean(
        "The test accuracy of 98.91% demonstrates strong generalisation. The small gap between "
        "validation (~99.2%) and test accuracy confirms the model generalises well without overfitting."
    ))

    pdf.subsection_heading("C", "Performance Comparison")
    pdf.add_table(
        "PERFORMANCE COMPARISON WITH BASELINE METHODS",
        ["Method", "Acc. (%)", "Params"],
        [
            ["k-NN", "96.9", "--"],
            ["SVM (RBF)", "98.6", "--"],
            ["MLP", "97.8", "~236K"],
            ["Proposed CNN", "98.91", "~1.2M"],
            ["LeNet-5", "99.2", "~60K"],
            ["Deep CNN [13]", "99.65", "~10M"],
        ],
        col_widths=[20, 16, 16],
    )

    pdf.subsection_heading("D", "Per-Class Classification Report")
    pdf.add_table(
        "PER-CLASS CLASSIFICATION REPORT",
        ["Digit", "Prec.", "Recall", "F1", "Supp."],
        [
            ["0", "0.989", "0.993", "0.991", "980"],
            ["1", "0.994", "0.995", "0.994", "1135"],
            ["2", "0.980", "0.994", "0.987", "1032"],
            ["3", "0.989", "0.991", "0.990", "1010"],
            ["4", "0.993", "0.990", "0.991", "982"],
            ["5", "0.976", "0.991", "0.983", "892"],
            ["6", "0.995", "0.980", "0.987", "958"],
            ["7", "0.990", "0.989", "0.990", "1028"],
            ["8", "0.994", "0.988", "0.991", "974"],
            ["9", "0.991", "0.979", "0.985", "1009"],
            ["Avg", "0.989", "0.989", "0.989", "10000"],
        ],
        col_widths=[10, 10, 10, 10, 10],
    )

    pdf.body_text(clean(
        "Digit 1 achieves the highest recall (99.47%) due to its simple, distinctive stroke. "
        "Digit 9 has the lowest recall (97.92%), frequently confused with digit 4 due to similar "
        "upper-loop structures."
    ))

    pdf.subsection_heading("E", "Confusion Matrix and Per-Class Accuracy")
    pdf.add_figure(
        os.path.join(IMAGES_DIR, "confusion_matrix.png"),
        "Confusion matrix showing correct and incorrect predictions per digit class.",
        width=pdf.col_width * 0.90,
    )
    pdf.add_figure(
        os.path.join(IMAGES_DIR, "per_class_accuracy.png"),
        "Per-digit accuracy. Digit 1 is highest (99.47%), Digit 9 lowest (97.92%).",
        width=pdf.col_width * 0.90,
    )

    pdf.subsection_heading("F", "Analysis of Misclassifications")
    pdf.body_text(clean(
        "The confusion matrix reveals common misclassification patterns:"
    ))
    misclass = [
        "6 -> 5: 9 samples, due to similar curved stroke patterns.",
        "9 -> 4: 6 samples, upper loop of 9 resembles angular 4.",
        "9 -> 5: 6 samples, particularly with open-top writing styles.",
        "0 -> 2: 6 samples, due to slanted oval shapes.",
        "4 -> 9 and 7 -> 2: 5 instances each, structural similarities.",
    ]
    for m in misclass:
        pdf.bullet_item(clean(m))

    pdf.body_text(clean(
        "These ambiguities often arise from genuinely ambiguous handwriting where even human "
        "annotators may disagree."
    ))

    pdf.subsection_heading("G", "Computational Efficiency")
    pdf.add_table(
        "COMPUTATIONAL PERFORMANCE METRICS",
        ["Metric", "Value"],
        [
            ["Training time", "~3 min (CPU)"],
            ["Inference time", "< 5 ms / image"],
            ["Model size", "~14 MB (.keras)"],
            ["Memory", "~50 MB"],
        ],
        col_widths=[24, 32],
    )

    # ── VI. DEPLOYMENT ──
    pdf.section_heading(6, "Deployment")

    pdf.subsection_heading("A", "Web Application Architecture")
    pdf.body_text(clean(
        "The trained CNN model was deployed as a real-time web application using Streamlit. The "
        "application consists of: (1) a frontend with a drawable HTML5 canvas via "
        "streamlit-drawable-canvas, (2) a backend with the Keras model cached for fast inference, "
        "and (3) a processing pipeline: canvas -> PIL image -> grayscale -> resize 28x28 -> "
        "normalise -> CNN prediction -> confidence visualisation."
    ))

    pdf.subsection_heading("B", "Real-Time Preprocessing")
    pdf.body_text(clean(
        "Custom images undergo: RGBA to grayscale conversion, resizing to 28x28 with Lanczos "
        "interpolation, normalisation to [0, 1], and reshaping to (1, 28, 28, 1) tensor."
    ))

    # ── VII. DISCUSSION ──
    pdf.section_heading(7, "Discussion")

    pdf.subsection_heading("A", "Strengths")
    pdf.body_text(clean(
        "1) High accuracy (98.91%) with only 9 layers and ~1.2M parameters. "
        "2) Effective regularisation via Dropout + BatchNorm preventing overfitting. "
        "3) Fast training (~3 min CPU) and inference (<5 ms). "
        "4) End-to-end practical deployment through Streamlit."
    ))

    pdf.subsection_heading("B", "Limitations")
    pdf.body_text(clean(
        "1) MNIST-specific training -- performance on unconstrained real-world images would be lower. "
        "2) Single-digit recognition only -- multi-digit reading requires segmentation. "
        "3) Domain gap between canvas-drawn digits and MNIST distribution."
    ))

    pdf.subsection_heading("C", "Proposed Improvements")
    pdf.body_text(clean(
        "1) Data augmentation (rotation +/-10, translation, zoom, shear) for improved robustness [24]. "
        "2) Deeper architecture with additional convolutional blocks for 99.5%+ accuracy. "
        "3) Learning rate scheduling via ReduceLROnPlateau. "
        "4) Ensemble of 3-5 models for 0.1-0.3% error reduction [16]. "
        "5) Residual connections and Capsule Networks [17] for advanced feature learning."
    ))

    # ── VIII. REAL-WORLD APPLICATIONS ──
    pdf.section_heading(8, "Real-World Applications")
    pdf.add_table(
        "REAL-WORLD APPLICATIONS OF HANDWRITTEN DIGIT RECOGNITION",
        ["Domain", "Application", "Scale"],
        [
            ["Postal", "ZIP code reading", "Billions/yr"],
            ["Banking", "Cheque recognition", "Millions/day"],
            ["Healthcare", "Prescription reading", "Hospital"],
            ["Education", "Exam grading", "Institutional"],
            ["Government", "Tax/census digitisation", "National"],
            ["Transport", "License plate digits", "City-wide"],
            ["Mobile", "Handwriting input", "Billions"],
            ["Security", "CAPTCHA recognition", "Web-scale"],
        ],
        col_widths=[16, 22, 18],
    )

    # ── IX. CONCLUSION ──
    pdf.section_heading(9, "Conclusion")
    pdf.body_text(clean(
        "This paper presented a CNN-based approach for handwritten digit recognition using the MNIST "
        "benchmark dataset. The proposed architecture, comprising two convolutional layers, max-pooling, "
        "batch normalisation, and dropout regularisation, achieved a test accuracy of 98.91% -- "
        "demonstrating that a relatively simple and well-regularised CNN can deliver high accuracy."
    ))
    pdf.body_text(clean(
        "Key contributions include: (1) a clearly documented and reproducible CNN implementation, "
        "(2) comprehensive analysis of training dynamics and regularisation, (3) practical deployment "
        "in a real-time web application, and (4) discussion of limitations and improvement proposals."
    ))
    pdf.body_text(clean(
        "Future work will focus on multi-digit recognition, training on more challenging datasets "
        "(EMNIST, SVHN), and exploring lightweight architectures for mobile deployment through model "
        "quantisation and knowledge distillation."
    ))

    # ── REFERENCES ──
    refs = [
        '[1] R. Plamondon and S. N. Srihari, "Online and off-line handwriting recognition: a comprehensive survey," IEEE Trans. PAMI, vol. 22, no. 1, pp. 63-84, 2000.',
        '[2] Y. LeCun, Y. Bengio, and G. Hinton, "Deep learning," Nature, vol. 521, pp. 436-444, 2015.',
        '[3] I. Goodfellow, Y. Bengio, and A. Courville, Deep Learning. MIT Press, 2016.',
        '[4] S. Impedovo et al., "Optical character recognition -- a survey," IJPRAI, vol. 5, pp. 1-24, 1991.',
        '[5] G. Dimauro et al., "Automatic bankcheck processing," IJPRAI, vol. 11, pp. 467-504, 1997.',
        '[6] V. Mitra and C. J. Acharya, "Gesture recognition: A survey," IEEE Trans. SMC, vol. 37, pp. 311-324, 2007.',
        '[7] A. Graves et al., "A novel connectionist system for unconstrained handwriting recognition," IEEE Trans. PAMI, vol. 31, pp. 855-868, 2009.',
        '[8] V. Vapnik, The Nature of Statistical Learning Theory. Springer, 1995.',
        '[9] T. M. Cover and P. E. Hart, "Nearest neighbor pattern classification," IEEE Trans. IT, vol. 13, pp. 21-27, 1967.',
        '[10] L. Breiman, "Random forests," Machine Learning, vol. 45, pp. 5-32, 2001.',
        '[11] Y. LeCun et al., "Gradient-based learning applied to document recognition," Proc. IEEE, vol. 86, pp. 2278-2324, 1998.',
        '[12] K. Hornik et al., "Multilayer feedforward networks are universal approximators," Neural Networks, vol. 2, pp. 359-366, 1989.',
        '[13] D. C. Ciresan et al., "Deep, big, simple neural nets for handwritten digit recognition," Neural Computation, vol. 22, pp. 3207-3220, 2010.',
        '[14] L. Wan et al., "Regularization of neural networks using DropConnect," Proc. ICML, pp. 1058-1066, 2013.',
        '[15] S. Ioffe and C. Szegedy, "Batch normalization," Proc. ICML, pp. 448-456, 2015.',
        '[16] L. K. Hansen and P. Salamon, "Neural network ensembles," IEEE Trans. PAMI, vol. 12, pp. 993-1001, 1990.',
        '[17] S. Sabour et al., "Dynamic routing between capsules," NeurIPS, pp. 3856-3866, 2017.',
        '[18] D. P. Kingma and J. Ba, "Adam: A method for stochastic optimization," Proc. ICLR, 2015.',
        '[19] K. Simonyan and A. Zisserman, "Very deep convolutional networks," Proc. ICLR, 2015.',
        '[20] V. Nair and G. E. Hinton, "Rectified linear units improve restricted Boltzmann machines," Proc. ICML, pp. 807-814, 2010.',
        '[21] D. Scherer et al., "Evaluation of pooling operations in convolutional architectures," Proc. ICANN, pp. 92-101, 2010.',
        '[22] N. Srivastava et al., "Dropout: a simple way to prevent neural networks from overfitting," JMLR, vol. 15, pp. 1929-1958, 2014.',
        '[23] D. P. Kingma and J. Ba, "Adam: A method for stochastic optimization," arXiv:1412.6980, 2014.',
        '[24] A. Krizhevsky et al., "ImageNet classification with deep convolutional neural networks," NeurIPS, pp. 1097-1105, 2012.',
    ]
    pdf.add_references(refs)

    # ─── Save ──────────────────────────────────────────────────────
    pdf.output(PDF_PATH)
    file_size = os.path.getsize(PDF_PATH) / 1024
    print(f"\n{'='*55}")
    print(f"  IEEE-format PDF generated successfully!")
    print(f"  File: {PDF_PATH}")
    print(f"  Size: {file_size:.1f} KB")
    print(f"  Pages: {pdf.page_no()}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    build_pdf()
