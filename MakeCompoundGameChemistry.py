import cv2
import os
import random
import re
import requests
from tkinter import Tk, Button, Label, Frame, Entry, StringVar, messagebox, Toplevel, Text, Scrollbar, RIGHT, Y, END, DISABLED, NORMAL
from PIL import Image, ImageTk

# Tooltip helper class
class CreateToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify='left',
                      background="#ffffe0", relief='solid', borderwidth=1,
                      font=("tahoma", "10", "normal")) # Increased font size for tooltip
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# Map all 118 elements to their full names
ELEMENTS_FULL_NAMES = {
    "H": "Hydrogen", "He": "Helium", "Li": "Lithium", "Be": "Beryllium",
    "B": "Boron", "C": "Carbon", "N": "Nitrogen", "O": "Oxygen",
    "F": "Fluorine", "Ne": "Neon", "Na": "Sodium", "Mg": "Magnesium",
    "Al": "Aluminium", "Si": "Silicon", "P": "Phosphorus", "S": "Sulfur",
    "Cl": "Chlorine", "Ar": "Argon", "K": "Potassium", "Ca": "Calcium",
    "Sc": "Scandium", "Ti": "Titanium", "V": "Vanadium", "Cr": "Chromium",
    "Mn": "Manganese", "Fe": "Iron", "Co": "Cobalt", "Ni": "Nickel",
    "Cu": "Copper", "Zn": "Zinc", "Ga": "Gallium", "Ge": "Germanium",
    "As": "Arsenic", "Se": "Selenium", "Br": "Bromine", "Kr": "Krypton",
    "Rb": "Rubidium", "Sr": "Strontium", "Y": "Yttrium", "Zr": "Zirconium",
    "Nb": "Niobium", "Mo": "Molybdenum", "Tc": "Technetium", "Ru": "Ruthenium",
    "Rh": "Rhodium", "Pd": "Palladium", "Ag": "Silver", "Cd": "Cadmium",
    "In": "Indium", "Sn": "Tin", "Sb": "Antimony", "Te": "Tellurium",
    "I": "Iodine", "Xe": "Xenon", "Cs": "Cesium", "Ba": "Barium",
    "La": "Lanthanum", "Ce": "Cerium", "Pr": "Praseodymium", "Nd": "Neodymium",
    "Pm": "Promethium", "Sm": "Samarium", "Eu": "Europium", "Gd": "Gadolinium",
    "Tb": "Terbium", "Dy": "Dysprosium", "Ho": "Holmium", "Er": "Erbium",
    "Tm": "Thulium", "Yb": "Ytterbium", "Lu": "Lutetium", "Hf": "Hafnium",
    "Ta": "Tantalum", "W": "Tungsten", "Re": "Rhenium", "Os": "Osmium",
    "Ir": "Iridium", "Pt": "Platinum", "Au": "Gold", "Hg": "Mercury",
    "Tl": "Thallium", "Pb": "Lead", "Bi": "Bismuth", "Po": "Polonium",
    "At": "Astatine", "Rn": "Radon", "Fr": "Francium", "Ra": "Radium",
    "Ac": "Actinium", "Th": "Thorium", "Pa": "Protactinium", "U": "Uranium",
    "Np": "Neptunium", "Pu": "Plutonium", "Am": "Americium", "Cm": "Curium",
    "Bk": "Berkelium", "Cf": "Californium", "Es": "Einsteinium", "Fm": "Fermium",
    "Md": "Mendelevium", "No": "Nobelium", "Lr": "Lawrencium", "Rf": "Rutherfordium",
    "Db": "Dubnium", "Sg": "Seaborgium", "Bh": "Bohrium", "Hs": "Hassium",
    "Mt": "Meitnerium", "Ds": "Darmstadtium", "Rg": "Roentgenium", "Cn": "Copernicium",
    "Nh": "Nihonium", "Fl": "Flerovium", "Mc": "Moscovium", "Lv": "Livermorium",
    "Ts": "Tennessine", "Og": "Oganesson"
}

# Known real compounds and their uses
COMMON_COMPOUNDS = {
    # Existing compounds would be here...
    "CH4": {
        "elements": {"C", "H"},
        "uses": "Natural gas fuel; heating and electricity generation; chemical feedstock.",
        "advantages": "Efficient energy source; relatively clean burning compared to other fossil fuels.",
        "disadvantages": "Potent greenhouse gas; explosive; non-renewable."
    },
    "C2H6": {
        "elements": {"C", "H"},
        "uses": "Fuel; refrigerant; raw material for plastics (ethylene production).",
        "advantages": "Cleaner burning than methane; used in various industrial processes.",
        "disadvantages": "Flammable; contributes to greenhouse gas emissions."
    },
    "C3H8": {
        "elements": {"C", "H"},
        "uses": "LPG (Liquefied Petroleum Gas) fuel for heating, cooking, and vehicles.",
        "advantages": "Portable energy source; clean burning; efficient.",
        "disadvantages": "Flammable; requires pressurized storage; non-renewable."
    },
    "C4H10": {
        "elements": {"C", "H"},
        "uses": "Fuel (component of LPG and gasoline); aerosol propellant; refrigerant.",
        "advantages": "Versatile fuel and industrial chemical.",
        "disadvantages": "Highly flammable; contributes to greenhouse gas emissions."
    },
    "C2H4": {
        "elements": {"C", "H"},
        "uses": "Ethylene; primary feedstock for polyethylene plastic; fruit ripening agent.",
        "advantages": "Key building block for plastics and other chemicals; natural plant hormone.",
        "disadvantages": "Flammable gas; can act as an asphyxiant."
    },
    "C3H6": {
        "elements": {"C", "H"},
        "uses": "Propylene; feedstock for polypropylene plastic; used in resins and fibers.",
        "advantages": "Essential monomer for various plastics and materials.",
        "disadvantages": "Highly flammable gas; potential respiratory irritant."
    },
    "C2H2": {
        "elements": {"C", "H"},
        "uses": "Acetylene; fuel for welding and cutting; chemical synthesis (e.g., vinyl chloride).",
        "advantages": "Produces very hot flame for industrial applications.",
        "disadvantages": "Highly unstable and explosive at high pressures; requires careful handling."
    },
    "C6H6": {
        "elements": {"C", "H"},
        "uses": "Benzene; solvent; precursor to plastics, synthetic fibers, and rubber.",
        "advantages": "Important industrial solvent and chemical intermediate.",
        "disadvantages": "Carcinogenic; highly flammable; harmful if inhaled or absorbed."
    },
    "C7H8": {
        "elements": {"C", "H"},
        "uses": "Toluene; solvent in paints, coatings, and adhesives; component of gasoline.",
        "advantages": "Effective solvent; less toxic than benzene, but still hazardous.",
        "disadvantages": "Flammable; can cause neurological effects with prolonged exposure."
    },
    "C8H10": { # Xylene (isomer mixture)
        "elements": {"C", "H"},
        "uses": "Solvent in printing, rubber, and leather industries; component of gasoline.",
        "advantages": "Good solvent properties; useful in various manufacturing processes.",
        "disadvantages": "Flammable; potential for respiratory and neurological effects."
    },
    "C10H8": {
        "elements": {"C", "H"},
        "uses": "Naphthalene; mothballs; chemical intermediate for dyes, resins, and insecticides.",
        "advantages": "Effective pest deterrent; versatile chemical building block.",
        "disadvantages": "Flammable; harmful if ingested or inhaled; potential carcinogen."
    },
    "H2O": {
        "elements": {"H", "O"},
        "uses": "Essential for life; solvent in biological and chemical processes; drinking water.",
        "advantages": "Non-toxic, abundant, supports life and industry.",
        "disadvantages": "Excess can cause flooding; corrosive in some conditions."
    },
    "H2O2": {
        "elements": {"H", "O"},
        "uses": "Disinfectant and antiseptic (e.g., for wounds, mouthwash); bleaching agent (for hair, textiles, paper pulp); oxidizer in chemical synthesis; component of rocket fuels; wastewater treatment.",
        "advantages": "Decomposes into water and oxygen (environmentally friendly byproducts); effective oxidizing agent.",
        "disadvantages": "Corrosive in concentrated forms; can cause skin/eye irritation; unstable and decomposes (especially with light/impurities); dangerous if ingested in high concentrations."
    },
    "NaCl": {
        "elements": {"Na", "Cl"},
        "uses": "Table salt; food seasoning and preservative; industrial chemical.",
        "advantages": "Inexpensive, essential mineral.",
        "disadvantages": "Excess consumption can cause hypertension."
    },
    "CO2": {
        "elements": {"C", "O"},
        "uses": "Carbonation in beverages; fire extinguishers; photosynthesis.",
        "advantages": "Non-flammable, essential for plant life.",
        "disadvantages": "Greenhouse gas contributing to climate change."
    }
    ,
    "NH3": {
        "elements": {"N", "H"},
        "uses": "Fertilizer production; refrigeration; cleaning agents.",
        "advantages": "Boosts crop yields.",
        "disadvantages": "Toxic and corrosive; hazardous if inhaled."
    },
    "CaCl2": {
        "elements": {"Ca", "Cl"},
        "uses": "De-icing roads; dust control; food additive.",
        "advantages": "Effective ice melter.",
        "disadvantages": "Corrosive to metals; environmental contamination risks."
    },
    "HCl": {
        "elements": {"H", "Cl"},
        "uses": "Industrial cleaning; PVC manufacturing; pH regulation.",
        "advantages": "Strong acid, versatile industrial chemical.",
        "disadvantages": "Corrosive; harmful if inhaled or contacted."
    },
    "C6H12O6": {
        "elements": {"C", "H", "O"},
        "uses": "Glucose; energy source for living cells.",
        "advantages": "Essential nutrient; provides energy.",
        "disadvantages": "Excess consumption linked to diabetes and obesity."
    },
    "NaOH": {
        "elements": {"Na", "O", "H"},
        "uses": "Drain cleaner; soap making; chemical manufacturing.",
        "advantages": "Strong base; effective cleaning agent.",
        "disadvantages": "Highly corrosive; causes burns."
    },
    "Fe2O3": {
        "elements": {"Fe", "O"},
        "uses": "Rust (iron oxide); pigment; iron ore.",
        "advantages": "Widely available iron source.",
        "disadvantages": "Corrosion damages metal structures."
    },
    "H2SO4": {
        "elements": {"H", "S", "O"},
        "uses": "Battery acid; fertilizer production; chemical synthesis.",
        "advantages": "Strong acid; industrially important.",
        "disadvantages": "Highly corrosive; dangerous to handle."
    },
    "CH3COOH": {
        "elements": {"C", "H", "O"},
        "uses": "Acetic acid; vinegar; food preservative.",
        "advantages": "Safe in dilute form; flavoring agent.",
        "disadvantages": "Concentrated acid is corrosive."
    },
    "NaHCO3": {
        "elements": {"Na", "H", "C", "O"},
        "uses": "Baking soda; antacid; cleaning agent.",
        "advantages": "Non-toxic; versatile household chemical.",
        "disadvantages": "Can cause alkalosis if overused."
    },
    "C2H5OH": {
        "elements": {"C", "H", "O"},
        "uses": "Ethanol; alcoholic beverages; solvent; fuel.",
        "advantages": "Renewable biofuel; disinfectant.",
        "disadvantages": "Intoxicating; flammable."
    },
    "Na2CO3": {
        "elements": {"Na", "C", "O"},
        "uses": "Washing soda; glass making; water softener.",
        "advantages": "Effective cleaning agent.",
        "disadvantages": "Can irritate skin and eyes."
    },
    "KNO3": {
        "elements": {"K", "N", "O"},
        "uses": "Fertilizer; food preservative; gunpowder component.",
        "advantages": "Provides essential nutrients to plants.",
        "disadvantages": "Explosive under some conditions."
    },
    # --- Additional Compounds Below ---
    "C12H22O11": {
        "elements": {"C", "H", "O"},
        "uses": "Sucrose (table sugar); food sweetener; energy source.",
        "advantages": "Common sweetener, readily available energy.",
        "disadvantages": "Excess consumption contributes to obesity, diabetes, and dental issues."
    },
    "CaCO3": {
        "elements": {"Ca", "C", "O"},
        "uses": "Limestone, marble, chalk; antacid; building material; filler in plastics and paints.",
        "advantages": "Abundant, relatively non-toxic, versatile in applications.",
        "disadvantages": "Can contribute to hard water issues; reacts with acids to produce CO2."
    },
    "N2O": {
        "elements": {"N", "O"},
        "uses": "Nitrous oxide (laughing gas); anesthetic in dentistry; propellant in aerosol cans.",
        "advantages": "Effective anesthetic; non-flammable.",
        "disadvantages": "Potent greenhouse gas; can cause oxygen deprivation if misused."
    },
    "SiO2": {
        "elements": {"Si", "O"},
        "uses": "Silicon dioxide (silica); main component of sand and quartz; glass manufacturing; abrasive.",
        "advantages": "Abundant, chemically stable, high melting point.",
        "disadvantages": "Inhalation of fine particles can cause silicosis; not easily biodegradable."
    },
    "K2CO3": {
        "elements": {"K", "C", "O"},
        "uses": "Potassium carbonate (potash); glass and soap manufacturing; fertilizer.",
        "advantages": "Source of potassium for plants; water-soluble.",
        "disadvantages": "Can irritate skin and eyes; corrosive in concentrated solutions."
    },
    "Mg(OH)2": {
        "elements": {"Mg", "O", "H"},
        "uses": "Magnesium hydroxide (Milk of Magnesia); antacid; laxative; flame retardant.",
        "advantages": "Effective for indigestion relief; relatively mild.",
        "disadvantages": "Can cause diarrhea; large doses can lead to hypermagnesemia."
    },
    
    "FeS2": {
        "elements": {"Fe", "S"},
        "uses": "Iron pyrite (Fool's Gold); mineral specimen; source of sulfur for sulfuric acid.",
        "advantages": "Distinctive appearance, source of sulfur.",
        "disadvantages": "Oxidizes to produce sulfuric acid (acid mine drainage); no economic value as gold."
    },
    "CH3OH": {
        "elements": {"C", "H", "O"},
        "uses": "Methanol (wood alcohol); solvent; antifreeze; fuel (biofuel).",
        "advantages": "Clean-burning fuel; versatile solvent.",
        "disadvantages": "Highly toxic if ingested; can cause blindness or death; flammable."
    },
    "CuO": {
        "elements": {"Cu", "O"},
        "uses": "Copper(II) oxide; pigment (blue/green in glass/ceramics); catalyst; insecticide.",
        "advantages": "Stable, good pigment.",
        "disadvantages": "Toxic if ingested; environmental concerns in high concentrations."
    },
    "Al2O3": {
        "elements": {"Al", "O"},
        "uses": "Aluminum oxide (alumina); abrasive; ceramics; component of bauxite ore.",
        "advantages": "Very hard material; high melting point; chemically stable.",
        "disadvantages": "Energy-intensive production; dust inhalation can cause respiratory issues."
    },
    "ZnO": {
        "elements": {"Zn", "O"},
        "uses": "Zinc oxide; sunscreen; diaper rash cream; rubber additive; pigment.",
        "advantages": "Broad-spectrum UV absorber; anti-inflammatory properties.",
        "disadvantages": "Nanosized particles can be controversial; environmental impact concerns."
    },
    
    "KOH": {
        "elements": {"K", "O", "H"},
        "uses": "Potassium hydroxide (caustic potash); used in soap making, as an electrolyte in alkaline batteries, and in chemical synthesis.",
        "advantages": "Strong base, highly reactive for various industrial processes.",
        "disadvantages": "Highly corrosive, can cause severe burns; reacts exothermically with water."
    },
    "MgCl2": {
        "elements": {"Mg", "Cl"},
        "uses": "Magnesium chloride; de-icing agent, dust control, magnesium metal production, food additive (e.g., tofu coagulant).",
        "advantages": "Effective de-icer, less corrosive than sodium chloride for some applications.",
        "disadvantages": "Can be corrosive to metals; can contribute to water hardness."
    },
    "CuSO4": {
        "elements": {"Cu", "S", "O"},
        "uses": "Copper(II) sulfate; fungicide, algicide, herbicide, in electroplating, and as a raw material for other copper compounds.",
        "advantages": "Effective against fungal diseases and algae; relatively common and inexpensive.",
        "disadvantages": "Toxic if ingested; harmful to aquatic life in high concentrations; can irritate skin and eyes."
    },
    "AlCl3": {
        "elements": {"Al", "Cl"},
        "uses": "Aluminum chloride; Lewis acid catalyst in organic chemistry (e.g., Friedel-Crafts reactions), antiperspirant ingredient.",
        "advantages": "Potent catalyst for certain reactions; effective antiperspirant.",
        "disadvantages": "Corrosive; reacts violently with water; can cause skin and respiratory irritation."
    },
    "ZnCl2": {
        "elements": {"Zn", "Cl"},
        "uses": "Zinc chloride; flux for soldering, wood preservative, in dry cell batteries, and as a catalyst in organic synthesis.",
        "advantages": "Effective flux for removing oxides; good wood preservative.",
        "disadvantages": "Corrosive; can cause skin and eye irritation; harmful if ingested."
    },
    "FeCl3": {
        "elements": {"Fe", "Cl"},
        "uses": "Iron(III) chloride (ferric chloride); wastewater treatment (flocculant), etching agent for circuit boards, catalyst.",
        "advantages": "Effective coagulant for water purification; versatile etching agent.",
        "disadvantages": "Corrosive; can stain surfaces; harmful if ingested."
    },
    "Na2SO4": {
        "elements": {"Na", "S", "O"},
        "uses": "Sodium sulfate; in detergent manufacturing, Kraft paper production, glass industry, and as a laxative (Glauber's salt).",
        "advantages": "Common industrial chemical; relatively non-toxic.",
        "disadvantages": "Can cause digestive upset if ingested in large quantities; contributes to total dissolved solids in water."
    },
    "K2SO4": {
        "elements": {"K", "S", "O"},
        "uses": "Potassium sulfate; fertilizer (source of potassium and sulfur), in glass manufacturing.",
        "advantages": "Excellent source of potassium for plants, especially chloride-sensitive crops.",
        "disadvantages": "Less soluble than potassium chloride; can cause imbalances if over-applied."
    },
    "CaSO4": {
        "elements": {"Ca", "S", "O"},
        "uses": "Calcium sulfate (gypsum); plaster of Paris, drywall, fertilizer, food additive.",
        "advantages": "Common and inexpensive building material; provides calcium and sulfur to soil.",
        "disadvantages": "Dust can be respiratory irritant; contributes to hard water issues."
    },
    "NaNO3": {
        "elements": {"Na", "N", "O"},
        "uses": "Sodium nitrate; fertilizer, food preservative (curing meat), component of some solid rocket propellants.",
        "advantages": "Effective nitrogen fertilizer; inhibits bacterial growth in food.",
        "disadvantages": "Can contribute to methemoglobinemia in infants; potential for environmental contamination (nitrate leaching)."
    },
    "KNO2": {
        "elements": {"K", "N", "O"},
        "uses": "Potassium nitrite; food preservative (curing agent for meats), chemical reagent.",
        "advantages": "Effective antimicrobial agent in cured meats.",
        "disadvantages": "Can react to form nitrosamines, which are carcinogenic; toxic in high doses."
    },
    "Ca(NO3)2": {
        "elements": {"Ca", "N", "O"},
        "uses": "Calcium nitrate; fertilizer, component in concrete admixtures.",
        "advantages": "Provides soluble calcium and nitrogen for plants; accelerates concrete setting.",
        "disadvantages": "Can be deliquescent (absorbs moisture from air); potential for nitrate leaching."
    },
    "H2S": {
        "elements": {"H", "S"},
        "uses": "Hydrogen sulfide; industrial raw material (e.g., for sulfur production), analytical reagent.",
        "advantages": "Essential in some industrial processes.",
        "disadvantages": "Highly toxic gas with a rotten egg smell; flammable and corrosive."
    },
    "SO2": {
        "elements": {"S", "O"},
        "uses": "Sulfur dioxide; food preservative (antioxidant), disinfectant, in sulfuric acid production.",
        "advantages": "Effective preservative; key intermediate in chemical industry.",
        "disadvantages": "Respiratory irritant; contributes to acid rain; can cause allergic reactions in some individuals."
    },
    "CO": {
        "elements": {"C", "O"},
        "uses": "Carbon monoxide; fuel gas, reducing agent in metallurgy, chemical feedstock.",
        "advantages": "Useful in industrial processes.",
        "disadvantages": "Highly toxic gas; binds to hemoglobin, preventing oxygen transport; flammable."
    },
    "CH3Cl": {
        "elements": {"C", "H", "Cl"},
        "uses": "Chloromethane (methyl chloride); refrigerant, solvent, chemical intermediate.",
        "advantages": "Versatile industrial chemical.",
        "disadvantages": "Flammable gas; can be harmful if inhaled; ozone-depleting substance."
    },
    "CHCl3": {
        "elements": {"C", "H", "Cl"},
        "uses": "Chloroform; solvent, formerly an anesthetic, chemical reagent.",
        "advantages": "Good solvent for organic compounds.",
        "disadvantages": "Toxic if inhaled or ingested; potential carcinogen; can cause liver damage."
    },
    "CCl4": {
        "elements": {"C", "Cl"},
        "uses": "Carbon tetrachloride; formerly a cleaning agent and fire extinguisher, now primarily a chemical feedstock.",
        "advantages": "Good solvent.",
        "disadvantages": "Highly toxic; causes liver and kidney damage; ozone-depleting substance."
    },
    "C2HCl3": {
        "elements": {"C", "H", "Cl"},
        "uses": "Trichloroethylene (TCE); solvent for degreasing, dry cleaning.",
        "advantages": "Effective degreaser.",
        "disadvantages": "Toxic; potential carcinogen; environmental contaminant."
    }
    
}

def validate_formula_with_pubchem(formula):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/formula/{formula}/cids/JSON"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        if "IdentifierList" in data and "CID" in data["IdentifierList"]:
            return True # Formula recognized by PubChem
    except requests.exceptions.RequestException as e:
        print(f"PubChem API error: {e}") # For debugging
        pass
    return False

class ChemistryCardApp:
    def __init__(self, root, folder_path):
        self.root = root
        
        self.folder_path = folder_path
        
        # Set window to full screen
        self.root.title("Chemistry Card App")
        # For Windows
        if os.name == 'nt':
            self.root.state('zoomed')
        else: # For Linux/macOS
            width = self.root.winfo_screenwidth()
            height = self.root.winfo_screenheight()
            self.root.geometry(f"{width}x{height}+0+0")

        # Calculate card size based on screen height
        # This will make cards approximately 45% of the screen height (increased from 35%)
        self.screen_height = self.root.winfo_screenheight()
        self.card_height = int(self.screen_height * 0.50) # FURTHER INCREASED CARD HEIGHT
        self.card_width = int(self.card_height * (150/220)) # Maintain aspect ratio
        self.card_size = (self.card_width, self.card_height)
        
        self.images = self.load_images()

        self.score = 0
        self.time_left = 120 # 2 minutes in seconds
        self.timer_running = False
        self.discovered_compounds = set() # To store uniquely discovered compounds (e.g., {"H2O", "NaCl"})

        # --- Top Frame for Score and Timer ---
        self.top_frame = Frame(self.root)
        self.top_frame.pack(pady=self.screen_height * 0.01, fill='x') # Dynamic padding, fill width

        self.score_label = Label(self.top_frame, text=f"Score: {self.score}", font=("Arial", 20, "bold")) # Increased font size
        self.score_label.grid(row=0, column=0, padx=self.card_width * 0.1) # Dynamic padding

        self.timer_label = Label(self.top_frame, text=f"Time: {self.format_time(self.time_left)}", font=("Arial", 20, "bold")) # Increased font size
        self.timer_label.grid(row=0, column=1, padx=self.card_width * 0.1)
        
        # Configure columns to expand
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)


        # --- Card Display Frame ---
        self.card_frame = Frame(self.root)
        self.card_frame.pack(pady=self.screen_height * 0.02, expand=True) # Dynamic padding, expand for cards

        self.labels = []
        self.card_elements = []  # Current element symbols (e.g., ['Na', 'Cl', 'H', 'O'])

        for col in range(4):
            label = Label(self.card_frame, bd=4, relief="solid", bg="lightgray") # Increased border
            label.grid(row=0, column=col, padx=self.card_width * 0.05) # Dynamic padding
            self.labels.append(label)
            self.card_frame.grid_columnconfigure(col, weight=1) # Make columns expand

        # --- Control Frame (Entry and Buttons) ---
        self.control_frame = Frame(self.root)
        self.control_frame.pack(pady=self.screen_height * 0.01) # Dynamic padding

        self.reset_button = Button(self.control_frame, text="New Game", command=self.start_new_game, font=("Arial", 16)) # Increased font
        self.reset_button.grid(row=0, column=0, padx=self.card_width * 0.02)

        self.formula_var = StringVar()
        self.formula_entry = Entry(self.control_frame, textvariable=self.formula_var, width=25, font=("Arial", 16)) # Increased width and font
        self.formula_entry.grid(row=0, column=1, padx=self.card_width * 0.02)

        self.check_button = Button(self.control_frame, text="Check Formula", command=self.check_formula, font=("Arial", 16)) # Increased font
        self.check_button.grid(row=0, column=2, padx=self.card_width * 0.02)
        
        # --- Hint Button (NEW) ---
        self.hint_button = Button(self.control_frame, text="Hint", command=self.show_hint, font=("Arial", 16), bg="#ADD8E6") # Light Blue background
        self.hint_button.grid(row=0, column=3, padx=self.card_width * 0.02)

        # --- Discovered Compounds Display ---
        self.compounds_frame = Frame(self.root)
        self.compounds_frame.pack(pady=self.screen_height * 0.01, fill='both', expand=True, padx=self.card_width * 0.05) # Dynamic padding, fill and expand

        Label(self.compounds_frame, text="Discovered Compounds:", font=("Arial", 18, "bold")).pack(anchor='w', padx=5, pady=5) # Increased font
        
        self.discovered_text = Text(self.compounds_frame, wrap="word", height=8, bg="#e0e0e0", fg="blue", font=("Arial", 14)) # Increased height and font
        self.discovered_text.pack(side="left", fill="both", expand=True, padx=5)
        
        self.compounds_scrollbar = Scrollbar(self.compounds_frame, command=self.discovered_text.yview)
        self.compounds_scrollbar.pack(side="right", fill="y")
        self.discovered_text.config(yscrollcommand=self.compounds_scrollbar.set, state=DISABLED) # Initially disabled

        self.start_new_game() # Start a new game immediately

        # Bind click on cards to update formula input
        for label in self.labels:
            label.bind("<Button-1>", self.on_card_click)
            
        # Disable formula entry and check button initially until timer starts
        self.formula_entry.config(state=DISABLED)
        self.check_button.config(state=DISABLED)
        self.hint_button.config(state=DISABLED) # Disable hint button initially


    def load_images(self):
        files = os.listdir(self.folder_path)
        images = {}
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                symbol = os.path.splitext(file)[0].upper() # Ensure symbol is uppercase for consistency
                path = os.path.join(self.folder_path, file)
                img = cv2.imread(path)
                if img is not None:
                    # Resize based on dynamically calculated card_size
                    img = cv2.resize(img, self.card_size)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(img)
                    tk_img = ImageTk.PhotoImage(pil_img)
                    images[symbol] = tk_img
        return images

    def reset_cards(self):
        # Ensure we only pick elements for which we have images
        available_elements = list(self.images.keys())
        if len(available_elements) < 4:
            messagebox.showerror("Error", "Not enough element images in the 'cards' folder. Please add at least 4.")
            return

        self.card_elements = random.sample(available_elements, 4)
        for i, symbol in enumerate(self.card_elements):
            # Configure label dimensions to match the new card_size
            self.labels[i].config(image=self.images[symbol], width=self.card_width, height=self.card_height) 
            self.labels[i].image = self.images[symbol] # Keep a reference

            # Tooltip with full element name if available
            full_name = ELEMENTS_FULL_NAMES.get(symbol, "Unknown Element")
            CreateToolTip(self.labels[i], text=f"{symbol}: {full_name}")

        self.formula_var.set("")

    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def update_timer(self):
        if self.time_left > 0 and self.timer_running:
            self.time_left -= 1
            self.timer_label.config(text=f"Time: {self.format_time(self.time_left)}")
            self.root.after(1000, self.update_timer)
        elif self.time_left == 0 and self.timer_running:
            self.timer_running = False
            self.end_game()

    def start_new_game(self):
        self.score = 0
        self.time_left = 120
        self.discovered_compounds.clear() # Clear discovered compounds for a new game
        self.update_discovered_compounds_display() # Update display to be empty

        self.score_label.config(text=f"Score: {self.score}")
        self.timer_label.config(text=f"Time: {self.format_time(self.time_left)}")
        self.reset_cards() # Cards reset only on new game
        self.formula_var.set("")
        
        # Enable controls for the new game
        self.formula_entry.config(state=NORMAL)
        self.check_button.config(state=NORMAL)
        self.hint_button.config(state=NORMAL) # Enable hint button
        self.check_button.config(text="Check Formula") # Reset text if it was "Game Over"

        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def end_game(self):
        messagebox.showinfo("Game Over", f"Time's up! Your final score is: {self.score}\n\nDiscovered Compounds:\n{', '.join(sorted(list(self.discovered_compounds)))}")
        self.formula_entry.config(state=DISABLED)
        self.check_button.config(state=DISABLED)
        self.hint_button.config(state=DISABLED) # Disable hint button
        self.check_button.config(text="Game Over") # Indicate game state
        self.timer_running = False

    def update_discovered_compounds_display(self):
        self.discovered_text.config(state=NORMAL) # Enable to edit
        self.discovered_text.delete(1.0, END) # Clear existing text
        if self.discovered_compounds:
            # Sort compounds alphabetically for consistent display
            sorted_compounds = sorted(list(self.discovered_compounds))
            self.discovered_text.insert(END, ", ".join(sorted_compounds))
        self.discovered_text.config(state=DISABLED) # Disable again

    def check_formula(self):
        if not self.timer_running:
            messagebox.showinfo("Game Over", "The game has ended. Please start a new game.")
            return

        formula = self.formula_var.get().strip()
        if not formula:
            messagebox.showwarning("Input error", "Please enter a chemical formula.")
            return

        # Basic formula regex validation
        if not re.fullmatch(r'([A-Z][a-z]?\d*)+', formula):
            messagebox.showerror("Invalid formula", "Please enter a valid chemical formula using element symbols and numbers (e.g., H2O, NaCl).")
            self.formula_var.set("") # Clear entry for incorrect attempts
            return

        # Extract elements from the formula
        elements_in_formula = re.findall(r'[A-Z][a-z]?', formula)
        
        # Check if ALL elements in the entered formula are present in the displayed cards
        if not all(element in self.card_elements for element in elements_in_formula):
            messagebox.showerror("Invalid elements", "The formula contains elements not present in the displayed cards.")
            self.formula_var.set("") # Clear entry for incorrect attempts
            return

        normalized_formula = formula # Use original case for display and storage
        
        compound_is_new = False
        points_to_add = 0

        # Check if formula is in known compounds
        if normalized_formula in COMMON_COMPOUNDS:
            if normalized_formula not in self.discovered_compounds:
                compound_is_new = True
                points_to_add = 10 # Points for known compounds
            self.show_compound_info(normalized_formula)
        else:
            # Otherwise, validate with PubChem API
            valid = validate_formula_with_pubchem(normalized_formula)
            if valid:
                if normalized_formula not in self.discovered_compounds:
                    compound_is_new = True
                    points_to_add = 5 # Points for PubChem validated formulas
                self.show_compound_info(normalized_formula, known=False)
            else:
                messagebox.showerror("Invalid formula", "Formula not recognized as a real compound by PubChem.")
                self.formula_var.set("") # Clear entry for invalid attempts
                return # Stop processing if not valid

        # Update score and discovered compounds if it's a new unique compound
        if compound_is_new:
            self.score += points_to_add
            self.score_label.config(text=f"Score: {self.score}")
            self.discovered_compounds.add(normalized_formula)
            self.update_discovered_compounds_display()
            messagebox.showinfo("Success!", f"You discovered a new compound: {normalized_formula}! (+{points_to_add} points)")
        else:
            messagebox.showinfo("Already Discovered", f"You already discovered {normalized_formula}. No additional points.")

        # IMPORTANT: Cards are NOT reset here. They will only reset on "New Game" or "Game Over".
        self.formula_var.set("") # Clear the input after checking


    def show_compound_info(self, formula, known=True):
        info = COMMON_COMPOUNDS.get(formula, None)
        if known and info:
            uses = info["uses"]
            advantages = info["advantages"]
            disadvantages = info["disadvantages"]
            title = f"Info for {formula} (Known Compound)"
        else:
            uses = "No detailed information available in the local database."
            advantages = "N/A (Information from PubChem)"
            disadvantages = "N/A (Information from PubChem)"
            title = f"Info for {formula} (Validated by PubChem)"

        # Create a popup window with scrollable text
        popup = Toplevel(self.root)
        popup.title(title)
        
        # Make popup size relative to main screen
        popup_width = int(self.root.winfo_width() * 0.4)
        popup_height = int(self.root.winfo_height() * 0.5)
        popup.geometry(f"{popup_width}x{popup_height}")

        text = Text(popup, wrap="word", font=("Arial", 12)) # Increased font size
        scrollbar = Scrollbar(popup, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)

        text.insert(END, f"Formula: {formula}\n\n")
        text.insert(END, f"Real-world uses:\n{uses}\n\n")
        text.insert(END, f"Advantages:\n{advantages}\n\n")
        text.insert(END, f"Disadvantages:\n{disadvantages}\n")

        text.config(state='disabled')
        text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)







    def on_card_click(self, event):
        if not self.timer_running:  # Don't allow clicking if the game is over
            return

        # Find which label was clicked
        clicked_label = event.widget
        # Get the index of the clicked label within self.labels
        try:
            idx = self.labels.index(clicked_label)
            symbol = self.card_elements[idx]
            current_formula = self.formula_var.get()
            # Correct the casing of the element symbol before appending
            if len(symbol) > 1:
                symbol = symbol[0].upper() + symbol[1:].lower()  # First letter uppercase, rest lowercase
            else:
                symbol = symbol.upper() # Ensure single-letter elements are uppercase
            # Append the corrected element symbol to the formula entry
            self.formula_var.set(current_formula + symbol)
        except ValueError:
            # This might happen if the click isn't directly on a label in self.labels, though unlikely with proper binding.
            pass




    def show_hint(self):
        if not self.timer_running:
            messagebox.showinfo("Game Over", "The game has ended. Please start a new game.")
            return

        possible_compounds = []
        current_elements_set = set(self.card_elements)

        # Iterate through known compounds to find matches
        for formula, details in COMMON_COMPOUNDS.items():
            required_elements = details["elements"]
            # Check if all required elements for this compound are present in the current cards
            if required_elements.issubset(current_elements_set):
                # Optionally, you could also check for exact counts of elements if you want to be stricter
                # For simplicity, this checks if the *types* of elements are available.
                # E.g., for H2O, if 'H' and 'O' are present, it's a possible hint.
                possible_compounds.append((formula, details))
        
        # Create hint popup window
        hint_popup = Toplevel(self.root)
        hint_popup.title("Hint: Possible Compounds")
        
        # Make popup size relative to main screen
        popup_width = int(self.root.winfo_width() * 0.5)
        popup_height = int(self.root.winfo_height() * 0.6)
        hint_popup.geometry(f"{popup_width}x{popup_height}")

        hint_text_widget = Text(hint_popup, wrap="word", font=("Arial", 12))
        hint_scrollbar = Scrollbar(hint_popup, command=hint_text_widget.yview)
        hint_text_widget.configure(yscrollcommand=hint_scrollbar.set)

        if possible_compounds:
            hint_text_widget.insert(END, "Here are some known compounds you can form with the current elements:\n\n", "bold")
            
            # Sort compounds alphabetically for consistent display
            sorted_compounds = sorted(possible_compounds, key=lambda x: x[0])

            for formula, details in sorted_compounds:
                hint_text_widget.insert(END, f"--- {formula} ---\n", "header")
                hint_text_widget.insert(END, f"Elements: {', '.join(details['elements'])}\n")
                hint_text_widget.insert(END, f"Uses: {details['uses']}\n")
                hint_text_widget.insert(END, f"Advantages: {details['advantages']}\n")
                hint_text_widget.insert(END, f"Disadvantages: {details['disadvantages']}\n\n")
        else:
            hint_text_widget.insert(END, "No common compounds from the database can be formed with the current elements.\nTry to think of less common ones, or combine multiple of the same element!")
            hint_text_widget.insert(END, "\n\nRemember, you can also try formulas that PubChem might recognize, even if they aren't in our list!", "info")

        hint_text_widget.tag_configure("bold", font=("Arial", 12, "bold"))
        hint_text_widget.tag_configure("header", font=("Arial", 13, "bold"), foreground="darkblue")
        hint_text_widget.tag_configure("info", font=("Arial", 11, "italic"), foreground="gray")
        
        hint_text_widget.config(state='disabled')
        hint_text_widget.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        hint_scrollbar.pack(side=RIGHT, fill=Y)

if __name__ == "__main__":
    root = Tk()
    # Make sure you have a 'cards' folder in the same directory as this script,
    # containing image files named after element symbols (e.g., H.png, O.jpg, Na.jpeg).
    # For example, create a folder named 'Cards1' and place your element images inside it.
    folder_path = "cards2" 
    app = ChemistryCardApp(root, folder_path)
    root.mainloop()