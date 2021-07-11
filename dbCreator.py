from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient()
db=client.panipuriKartz
# Issue the serverStatus command and print the results
serverStatusResult=db.command("serverStatus")
#pprint(serverStatusResult)
 
data = db.city_wise_count
l = [
    {
        "city": "Port Blair",
        "value": 1
    },
    {
        "city": "Adoni",
        "value": 1
    },
    {
        "city": "Amalapuram",
        "value": 1
    },
    {
        "city": "Anakapalle",
        "value": 1
    },
    {
        "city": "Anantapur",
        "value": 1
    },
    {
        "city": "Bapatla",
        "value": 1
    },
    {
        "city": "Bheemunipatnam",
        "value": 1
    },
    {
        "city": "Bhimavaram",
        "value": 1
    },
    {
        "city": "Bobbili",
        "value": 1
    },
    {
        "city": "Chilakaluripet",
        "value": 1
    },
    {
        "city": "Chirala",
        "value": 1
    },
    {
        "city": "Chittoor",
        "value": 1
    },
    {
        "city": "Dharmavaram",
        "value": 1
    },
    {
        "city": "Eluru",
        "value": 1
    },
    {
        "city": "Gooty",
        "value": 1
    },
    {
        "city": "Gudivada",
        "value": 1
    },
    {
        "city": "Gudur",
        "value": 1
    },
    {
        "city": "Guntakal",
        "value": 1
    },
    {
        "city": "Guntur",
        "value": 1
    },
    {
        "city": "Hindupur",
        "value": 1
    },
    {
        "city": "Jaggaiahpet",
        "value": 1
    },
    {
        "city": "Jammalamadugu",
        "value": 1
    },
    {
        "city": "Kadapa",
        "value": 1
    },
    {
        "city": "Kadiri",
        "value": 1
    },
    {
        "city": "Kakinada",
        "value": 1
    },
    {
        "city": "Kandukur",
        "value": 1
    },
    {
        "city": "Kavali",
        "value": 1
    },
    {
        "city": "Kovvur",
        "value": 1
    },
    {
        "city": "Kurnool",
        "value": 1
    },
    {
        "city": "Macherla",
        "value": 1
    },
    {
        "city": "Machilipatnam",
        "value": 1
    },
    {
        "city": "Madanapalle",
        "value": 1
    },
    {
        "city": "Mandapeta",
        "value": 1
    },
    {
        "city": "Markapur",
        "value": 1
    },
    {
        "city": "Nagari",
        "value": 1
    },
    {
        "city": "Naidupet",
        "value": 1
    },
    {
        "city": "Nandyal",
        "value": 1
    },
    {
        "city": "Narasapuram",
        "value": 1
    },
    {
        "city": "Narasaraopet",
        "value": 1
    },
    {
        "city": "Narsipatnam",
        "value": 1
    },
    {
        "city": "Nellore",
        "value": 1
    },
    {
        "city": "Nidadavole",
        "value": 1
    },
    {
        "city": "Nuzvid",
        "value": 1
    },
    {
        "city": "Ongole",
        "value": 1
    },
    {
        "city": "Palacole",
        "value": 1
    },
    {
        "city": "Palasa Kasibugga",
        "value": 1
    },
    {
        "city": "Parvathipuram",
        "value": 1
    },
    {
        "city": "Pedana",
        "value": 1
    },
    {
        "city": "Peddapuram",
        "value": 1
    },
    {
        "city": "Pithapuram",
        "value": 1
    },
    {
        "city": "Ponnur",
        "value": 1
    },
    {
        "city": "Proddatur",
        "value": 1
    },
    {
        "city": "Punganur",
        "value": 1
    },
    {
        "city": "Puttur",
        "value": 1
    },
    {
        "city": "Rajahmundry",
        "value": 1
    },
    {
        "city": "Rajam",
        "value": 1
    },
    {
        "city": "Rajampet",
        "value": 1
    },
    {
        "city": "Ramachandrapuram",
        "value": 1
    },
    {
        "city": "Rayachoti",
        "value": 1
    },
    {
        "city": "Rayadurg",
        "value": 1
    },
    {
        "city": "Renigunta",
        "value": 1
    },
    {
        "city": "Repalle",
        "value": 1
    },
    {
        "city": "Salur",
        "value": 1
    },
    {
        "city": "Samalkot",
        "value": 1
    },
    {
        "city": "Sattenapalle",
        "value": 1
    },
    {
        "city": "Srikakulam",
        "value": 1
    },
    {
        "city": "Srikalahasti",
        "value": 1
    },
    {
        "city": "Srisailam Project (Right Flank Colony) Township",
        "value": 1
    },
    {
        "city": "Sullurpeta",
        "value": 1
    },
    {
        "city": "Tadepalligudem",
        "value": 1
    },
    {
        "city": "Tadpatri",
        "value": 1
    },
    {
        "city": "Tanuku",
        "value": 1
    },
    {
        "city": "Tenali",
        "value": 1
    },
    {
        "city": "Tirupati",
        "value": 1
    },
    {
        "city": "Tiruvuru",
        "value": 1
    },
    {
        "city": "Tuni",
        "value": 1
    },
    {
        "city": "Uravakonda",
        "value": 1
    },
    {
        "city": "Venkatagiri",
        "value": 1
    },
    {
        "city": "Vijayawada",
        "value": 1
    },
    {
        "city": "Vinukonda",
        "value": 1
    },
    {
        "city": "Visakhapatnam",
        "value": 1
    },
    {
        "city": "Vizianagaram",
        "value": 1
    },
    {
        "city": "Yemmiganur",
        "value": 1
    },
    {
        "city": "Yerraguntla",
        "value": 1
    },
    {
        "city": "Naharlagun",
        "value": 1
    },
    {
        "city": "Pasighat",
        "value": 1
    },
    {
        "city": "Barpeta",
        "value": 1
    },
    {
        "city": "Bongaigaon City",
        "value": 1
    },
    {
        "city": "Dhubri",
        "value": 1
    },
    {
        "city": "Dibrugarh",
        "value": 1
    },
    {
        "city": "Diphu",
        "value": 1
    },
    {
        "city": "Goalpara",
        "value": 1
    },
    {
        "city": "Guwahati",
        "value": 1
    },
    {
        "city": "Jorhat",
        "value": 1
    },
    {
        "city": "Karimganj",
        "value": 1
    },
    {
        "city": "Lanka",
        "value": 1
    },
    {
        "city": "Lumding",
        "value": 1
    },
    {
        "city": "Mangaldoi",
        "value": 1
    },
    {
        "city": "Mankachar",
        "value": 1
    },
    {
        "city": "Margherita",
        "value": 1
    },
    {
        "city": "Mariani",
        "value": 1
    },
    {
        "city": "Marigaon",
        "value": 1
    },
    {
        "city": "Nagaon",
        "value": 1
    },
    {
        "city": "Nalbari",
        "value": 1
    },
    {
        "city": "North Lakhimpur",
        "value": 1
    },
    {
        "city": "Rangia",
        "value": 1
    },
    {
        "city": "Sibsagar",
        "value": 1
    },
    {
        "city": "Silapathar",
        "value": 1
    },
    {
        "city": "Silchar",
        "value": 1
    },
    {
        "city": "Tezpur",
        "value": 1
    },
    {
        "city": "Tinsukia",
        "value": 1
    },
    {
        "city": "Araria",
        "value": 1
    },
    {
        "city": "Arrah",
        "value": 1
    },
    {
        "city": "Arwal",
        "value": 1
    },
    {
        "city": "Asarganj",
        "value": 1
    },
    {
        "city": "Aurangabad",
        "value": 1
    },
    {
        "city": "Bagaha",
        "value": 1
    },
    {
        "city": "Barh",
        "value": 1
    },
    {
        "city": "Begusarai",
        "value": 1
    },
    {
        "city": "Bettiah",
        "value": 1
    },
    {
        "city": "Bhabua",
        "value": 1
    },
    {
        "city": "Bhagalpur",
        "value": 1
    },
    {
        "city": "Buxar",
        "value": 1
    },
    {
        "city": "Chhapra",
        "value": 1
    },
    {
        "city": "Darbhanga",
        "value": 1
    },
    {
        "city": "Dehri-on-Sone",
        "value": 1
    },
    {
        "city": "Dumraon",
        "value": 1
    },
    {
        "city": "Forbesganj",
        "value": 1
    },
    {
        "city": "Gaya",
        "value": 1
    },
    {
        "city": "Gopalganj",
        "value": 1
    },
    {
        "city": "Hajipur",
        "value": 1
    },
    {
        "city": "Jamalpur",
        "value": 1
    },
    {
        "city": "Jamui",
        "value": 1
    },
    {
        "city": "Jehanabad",
        "value": 1
    },
    {
        "city": "Katihar",
        "value": 1
    },
    {
        "city": "Kishanganj",
        "value": 1
    },
    {
        "city": "Lakhisarai",
        "value": 1
    },
    {
        "city": "Lalganj",
        "value": 1
    },
    {
        "city": "Madhepura",
        "value": 1
    },
    {
        "city": "Madhubani",
        "value": 1
    },
    {
        "city": "Maharajganj",
        "value": 1
    },
    {
        "city": "Mahnar Bazar",
        "value": 1
    },
    {
        "city": "Makhdumpur",
        "value": 1
    },
    {
        "city": "Maner",
        "value": 1
    },
    {
        "city": "Manihari",
        "value": 1
    },
    {
        "city": "Marhaura",
        "value": 1
    },
    {
        "city": "Masaurhi",
        "value": 1
    },
    {
        "city": "Mirganj",
        "value": 1
    },
    {
        "city": "Mokameh",
        "value": 1
    },
    {
        "city": "Motihari",
        "value": 1
    },
    {
        "city": "Motipur",
        "value": 1
    },
    {
        "city": "Munger",
        "value": 1
    },
    {
        "city": "Murliganj",
        "value": 1
    },
    {
        "city": "Muzaffarpur",
        "value": 1
    },
    {
        "city": "Narkatiaganj",
        "value": 1
    },
    {
        "city": "Naugachhia",
        "value": 1
    },
    {
        "city": "Nawada",
        "value": 1
    },
    {
        "city": "Nokha",
        "value": 1
    },
    {
        "city": "Patna",
        "value": 1
    },
    {
        "city": "Piro",
        "value": 1
    },
    {
        "city": "Purnia",
        "value": 1
    },
    {
        "city": "Rafiganj",
        "value": 1
    },
    {
        "city": "Rajgir",
        "value": 1
    },
    {
        "city": "Ramnagar",
        "value": 1
    },
    {
        "city": "Raxaul Bazar",
        "value": 1
    },
    {
        "city": "Revelganj",
        "value": 1
    },
    {
        "city": "Rosera",
        "value": 1
    },
    {
        "city": "Saharsa",
        "value": 1
    },
    {
        "city": "Samastipur",
        "value": 1
    },
    {
        "city": "Sasaram",
        "value": 1
    },
    {
        "city": "Sheikhpura",
        "value": 1
    },
    {
        "city": "Sheohar",
        "value": 1
    },
    {
        "city": "Sherghati",
        "value": 1
    },
    {
        "city": "Silao",
        "value": 1
    },
    {
        "city": "Sitamarhi",
        "value": 1
    },
    {
        "city": "Siwan",
        "value": 1
    },
    {
        "city": "Sonepur",
        "value": 1
    },
    {
        "city": "Sugauli",
        "value": 1
    },
    {
        "city": "Sultanganj",
        "value": 1
    },
    {
        "city": "Supaul",
        "value": 1
    },
    {
        "city": "Warisaliganj",
        "value": 1
    },
    {
        "city": "Chandigarh",
        "value": 1
    },
    {
        "city": "Ambikapur",
        "value": 1
    },
    {
        "city": "Bhatapara",
        "value": 1
    },
    {
        "city": "Bhilai Nagar",
        "value": 1
    },
    {
        "city": "Bilaspur",
        "value": 1
    },
    {
        "city": "Chirmiri",
        "value": 1
    },
    {
        "city": "Dalli-Rajhara",
        "value": 1
    },
    {
        "city": "Dhamtari",
        "value": 1
    },
    {
        "city": "Durg",
        "value": 1
    },
    {
        "city": "Jagdalpur",
        "value": 1
    },
    {
        "city": "Korba",
        "value": 1
    },
    {
        "city": "Mahasamund",
        "value": 1
    },
    {
        "city": "Manendragarh",
        "value": 1
    },
    {
        "city": "Mungeli",
        "value": 1
    },
    {
        "city": "Naila Janjgir",
        "value": 1
    },
    {
        "city": "Raigarh",
        "value": 1
    },
    {
        "city": "Raipur",
        "value": 1
    },
    {
        "city": "Rajnandgaon",
        "value": 1
    },
    {
        "city": "Sakti",
        "value": 1
    },
    {
        "city": "Tilda Newra",
        "value": 1
    },
    {
        "city": "Silvassa",
        "value": 1
    },
    {
        "city": "Delhi",
        "value": 1
    },
    {
        "city": "New Delhi",
        "value": 1
    },
    {
        "city": "Mapusa",
        "value": 1
    },
    {
        "city": "Margao",
        "value": 1
    },
    {
        "city": "Marmagao",
        "value": 1
    },
    {
        "city": "Panaji",
        "value": 1
    },
    {
        "city": "Adalaj",
        "value": 1
    },
    {
        "city": "Ahmedabad",
        "value": 1
    },
    {
        "city": "Amreli",
        "value": 1
    },
    {
        "city": "Anand",
        "value": 1
    },
    {
        "city": "Anjar",
        "value": 1
    },
    {
        "city": "Ankleshwar",
        "value": 1
    },
    {
        "city": "Bharuch",
        "value": 1
    },
    {
        "city": "Bhavnagar",
        "value": 1
    },
    {
        "city": "Bhuj",
        "value": 1
    },
    {
        "city": "Deesa",
        "value": 1
    },
    {
        "city": "Dhoraji",
        "value": 1
    },
    {
        "city": "Godhra",
        "value": 1
    },
    {
        "city": "Jamnagar",
        "value": 1
    },
    {
        "city": "Kadi",
        "value": 1
    },
    {
        "city": "Kapadvanj",
        "value": 1
    },
    {
        "city": "Keshod",
        "value": 1
    },
    {
        "city": "Khambhat",
        "value": 1
    },
    {
        "city": "Lathi",
        "value": 1
    },
    {
        "city": "Limbdi",
        "value": 1
    },
    {
        "city": "Lunawada",
        "value": 1
    },
    {
        "city": "Mahesana",
        "value": 1
    },
    {
        "city": "Mahuva",
        "value": 1
    },
    {
        "city": "Manavadar",
        "value": 1
    },
    {
        "city": "Mandvi",
        "value": 1
    },
    {
        "city": "Mangrol",
        "value": 1
    },
    {
        "city": "Mansa",
        "value": 1
    },
    {
        "city": "Mahemdabad",
        "value": 1
    },
    {
        "city": "Modasa",
        "value": 1
    },
    {
        "city": "Morvi",
        "value": 1
    },
    {
        "city": "Nadiad",
        "value": 1
    },
    {
        "city": "Navsari",
        "value": 1
    },
    {
        "city": "Padra",
        "value": 1
    },
    {
        "city": "Palanpur",
        "value": 1
    },
    {
        "city": "Palitana",
        "value": 1
    },
    {
        "city": "Pardi",
        "value": 1
    },
    {
        "city": "Patan",
        "value": 1
    },
    {
        "city": "Petlad",
        "value": 1
    },
    {
        "city": "Porbandar",
        "value": 1
    },
    {
        "city": "Radhanpur",
        "value": 1
    },
    {
        "city": "Rajkot",
        "value": 1
    },
    {
        "city": "Rajpipla",
        "value": 1
    },
    {
        "city": "Rajula",
        "value": 1
    },
    {
        "city": "Ranavav",
        "value": 1
    },
    {
        "city": "Rapar",
        "value": 1
    },
    {
        "city": "Salaya",
        "value": 1
    },
    {
        "city": "Sanand",
        "value": 1
    },
    {
        "city": "Savarkundla",
        "value": 1
    },
    {
        "city": "Sidhpur",
        "value": 1
    },
    {
        "city": "Sihor",
        "value": 1
    },
    {
        "city": "Songadh",
        "value": 1
    },
    {
        "city": "Surat",
        "value": 1
    },
    {
        "city": "Talaja",
        "value": 1
    },
    {
        "city": "Thangadh",
        "value": 1
    },
    {
        "city": "Tharad",
        "value": 1
    },
    {
        "city": "Umbergaon",
        "value": 1
    },
    {
        "city": "Umreth",
        "value": 1
    },
    {
        "city": "Una",
        "value": 1
    },
    {
        "city": "Unjha",
        "value": 1
    },
    {
        "city": "Upleta",
        "value": 1
    },
    {
        "city": "Vadnagar",
        "value": 1
    },
    {
        "city": "Vadodara",
        "value": 1
    },
    {
        "city": "Valsad",
        "value": 1
    },
    {
        "city": "Vapi",
        "value": 1
    },
    {
        "city": "Veraval",
        "value": 1
    },
    {
        "city": "Vijapur",
        "value": 1
    },
    {
        "city": "Viramgam",
        "value": 1
    },
    {
        "city": "Visnagar",
        "value": 1
    },
    {
        "city": "Vyara",
        "value": 1
    },
    {
        "city": "Wadhwan",
        "value": 1
    },
    {
        "city": "Wankaner",
        "value": 1
    },
    {
        "city": "Bahadurgarh",
        "value": 1
    },
    {
        "city": "Bhiwani",
        "value": 1
    },
    {
        "city": "Charkhi Dadri",
        "value": 1
    },
    {
        "city": "Faridabad",
        "value": 1
    },
    {
        "city": "Fatehabad",
        "value": 1
    },
    {
        "city": "Gohana",
        "value": 1
    },
    {
        "city": "Gurgaon",
        "value": 1
    },
    {
        "city": "Hansi",
        "value": 1
    },
    {
        "city": "Hisar",
        "value": 1
    },
    {
        "city": "Jind",
        "value": 1
    },
    {
        "city": "Kaithal",
        "value": 1
    },
    {
        "city": "Karnal",
        "value": 1
    },
    {
        "city": "Ladwa",
        "value": 1
    },
    {
        "city": "Mahendragarh",
        "value": 1
    },
    {
        "city": "Mandi Dabwali",
        "value": 1
    },
    {
        "city": "Narnaul",
        "value": 1
    },
    {
        "city": "Narwana",
        "value": 1
    },
    {
        "city": "Palwal",
        "value": 1
    },
    {
        "city": "Panchkula",
        "value": 1
    },
    {
        "city": "Panipat",
        "value": 1
    },
    {
        "city": "Pehowa",
        "value": 1
    },
    {
        "city": "Pinjore",
        "value": 1
    },
    {
        "city": "Rania",
        "value": 1
    },
    {
        "city": "Ratia",
        "value": 1
    },
    {
        "city": "Rewari",
        "value": 1
    },
    {
        "city": "Rohtak",
        "value": 1
    },
    {
        "city": "Safidon",
        "value": 1
    },
    {
        "city": "Samalkha",
        "value": 1
    },
    {
        "city": "Sarsod",
        "value": 1
    },
    {
        "city": "Shahbad",
        "value": 1
    },
    {
        "city": "Sirsa",
        "value": 1
    },
    {
        "city": "Sohna",
        "value": 1
    },
    {
        "city": "Sonipat",
        "value": 1
    },
    {
        "city": "Taraori",
        "value": 1
    },
    {
        "city": "Thanesar",
        "value": 1
    },
    {
        "city": "Tohana",
        "value": 1
    },
    {
        "city": "Yamunanagar",
        "value": 1
    },
    {
        "city": "Mandi",
        "value": 1
    },
    {
        "city": "Nahan",
        "value": 1
    },
    {
        "city": "Palampur",
        "value": 1
    },
    {
        "city": "Shimla",
        "value": 1
    },
    {
        "city": "Solan",
        "value": 1
    },
    {
        "city": "Sundarnagar",
        "value": 1
    },
    {
        "city": "Anantnag",
        "value": 1
    },
    {
        "city": "Baramula",
        "value": 1
    },
    {
        "city": "Jammu",
        "value": 1
    },
    {
        "city": "Kathua",
        "value": 1
    },
    {
        "city": "Punch",
        "value": 1
    },
    {
        "city": "Rajauri",
        "value": 1
    },
    {
        "city": "Sopore",
        "value": 1
    },
    {
        "city": "Srinagar",
        "value": 1
    },
    {
        "city": "Udhampur",
        "value": 1
    },
    {
        "city": "Adityapur",
        "value": 1
    },
    {
        "city": "Bokaro Steel City",
        "value": 1
    },
    {
        "city": "Chaibasa",
        "value": 1
    },
    {
        "city": "Chatra",
        "value": 1
    },
    {
        "city": "Chirkunda",
        "value": 1
    },
    {
        "city": "Medininagar (Daltonganj)",
        "value": 1
    },
    {
        "city": "Deoghar",
        "value": 1
    },
    {
        "city": "Dhanbad",
        "value": 1
    },
    {
        "city": "Dumka",
        "value": 1
    },
    {
        "city": "Giridih",
        "value": 1
    },
    {
        "city": "Gumia",
        "value": 1
    },
    {
        "city": "Hazaribag",
        "value": 1
    },
    {
        "city": "Jamshedpur",
        "value": 1
    },
    {
        "city": "Jhumri Tilaiya",
        "value": 1
    },
    {
        "city": "Lohardaga",
        "value": 1
    },
    {
        "city": "Madhupur",
        "value": 1
    },
    {
        "city": "Mihijam",
        "value": 1
    },
    {
        "city": "Musabani",
        "value": 1
    },
    {
        "city": "Pakaur",
        "value": 1
    },
    {
        "city": "Patratu",
        "value": 1
    },
    {
        "city": "Phusro",
        "value": 1
    },
    {
        "city": "Ramgarh",
        "value": 1
    },
    {
        "city": "Ranchi",
        "value": 1
    },
    {
        "city": "Sahibganj",
        "value": 1
    },
    {
        "city": "Saunda",
        "value": 1
    },
    {
        "city": "Simdega",
        "value": 1
    },
    {
        "city": "Tenu dam-cum-Kathhara",
        "value": 1
    },
    {
        "city": "Adyar",
        "value": 1
    },
    {
        "city": "Afzalpur",
        "value": 1
    },
    {
        "city": "Arsikere",
        "value": 1
    },
    {
        "city": "Athni",
        "value": 1
    },
    {
        "city": "Bengaluru",
        "value": 1
    },
    {
        "city": "Belagavi",
        "value": 1
    },
    {
        "city": "Ballari",
        "value": 1
    },
    {
        "city": "Chikkamagaluru",
        "value": 1
    },
    {
        "city": "Davanagere",
        "value": 1
    },
    {
        "city": "Gokak",
        "value": 1
    },
    {
        "city": "Hubli-Dharwad",
        "value": 1
    },
    {
        "city": "Karwar",
        "value": 1
    },
    {
        "city": "Kolar",
        "value": 1
    },
    {
        "city": "Lakshmeshwar",
        "value": 1
    },
    {
        "city": "Lingsugur",
        "value": 1
    },
    {
        "city": "Maddur",
        "value": 1
    },
    {
        "city": "Madhugiri",
        "value": 1
    },
    {
        "city": "Madikeri",
        "value": 1
    },
    {
        "city": "Magadi",
        "value": 1
    },
    {
        "city": "Mahalingapura",
        "value": 1
    },
    {
        "city": "Malavalli",
        "value": 1
    },
    {
        "city": "Malur",
        "value": 1
    },
    {
        "city": "Mandya",
        "value": 1
    },
    {
        "city": "Mangaluru",
        "value": 1
    },
    {
        "city": "Manvi",
        "value": 1
    },
    {
        "city": "Mudalagi",
        "value": 1
    },
    {
        "city": "Mudabidri",
        "value": 1
    },
    {
        "city": "Muddebihal",
        "value": 1
    },
    {
        "city": "Mudhol",
        "value": 1
    },
    {
        "city": "Mulbagal",
        "value": 1
    },
    {
        "city": "Mundargi",
        "value": 1
    },
    {
        "city": "Nanjangud",
        "value": 1
    },
    {
        "city": "Nargund",
        "value": 1
    },
    {
        "city": "Navalgund",
        "value": 1
    },
    {
        "city": "Nelamangala",
        "value": 1
    },
    {
        "city": "Pavagada",
        "value": 1
    },
    {
        "city": "Piriyapatna",
        "value": 1
    },
    {
        "city": "Rabkavi Banhatti",
        "value": 1
    },
    {
        "city": "Raayachuru",
        "value": 1
    },
    {
        "city": "Ranebennuru",
        "value": 1
    },
    {
        "city": "Ramanagaram",
        "value": 1
    },
    {
        "city": "Ramdurg",
        "value": 1
    },
    {
        "city": "Ranibennur",
        "value": 1
    },
    {
        "city": "Robertson Pet",
        "value": 1
    },
    {
        "city": "Ron",
        "value": 1
    },
    {
        "city": "Sadalagi",
        "value": 1
    },
    {
        "city": "Sagara",
        "value": 1
    },
    {
        "city": "Sakaleshapura",
        "value": 1
    },
    {
        "city": "Sindagi",
        "value": 1
    },
    {
        "city": "Sanduru",
        "value": 1
    },
    {
        "city": "Sankeshwara",
        "value": 1
    },
    {
        "city": "Saundatti-Yellamma",
        "value": 1
    },
    {
        "city": "Savanur",
        "value": 1
    },
    {
        "city": "Sedam",
        "value": 1
    },
    {
        "city": "Shahabad",
        "value": 1
    },
    {
        "city": "Shahpur",
        "value": 1
    },
    {
        "city": "Shiggaon",
        "value": 1
    },
    {
        "city": "Shikaripur",
        "value": 1
    },
    {
        "city": "Shivamogga",
        "value": 1
    },
    {
        "city": "Surapura",
        "value": 1
    },
    {
        "city": "Shrirangapattana",
        "value": 1
    },
    {
        "city": "Sidlaghatta",
        "value": 1
    },
    {
        "city": "Sindhagi",
        "value": 1
    },
    {
        "city": "Sindhnur",
        "value": 1
    },
    {
        "city": "Sira",
        "value": 1
    },
    {
        "city": "Sirsi",
        "value": 1
    },
    {
        "city": "Siruguppa",
        "value": 1
    },
    {
        "city": "Srinivaspur",
        "value": 1
    },
    {
        "city": "Tarikere",
        "value": 1
    },
    {
        "city": "Tekkalakote",
        "value": 1
    },
    {
        "city": "Terdal",
        "value": 1
    },
    {
        "city": "Talikota",
        "value": 1
    },
    {
        "city": "Tiptur",
        "value": 1
    },
    {
        "city": "Tumkur",
        "value": 1
    },
    {
        "city": "Udupi",
        "value": 1
    },
    {
        "city": "Vijayapura",
        "value": 1
    },
    {
        "city": "Wadi",
        "value": 1
    },
    {
        "city": "Yadgir",
        "value": 1
    },
    {
        "city": "Mysore",
        "value": 1
    },
    {
        "city": "Adoor",
        "value": 1
    },
    {
        "city": "Alappuzha",
        "value": 1
    },
    {
        "city": "Attingal",
        "value": 1
    },
    {
        "city": "Chalakudy",
        "value": 1
    },
    {
        "city": "Changanassery",
        "value": 1
    },
    {
        "city": "Cherthala",
        "value": 1
    },
    {
        "city": "Chittur-Thathamangalam",
        "value": 1
    },
    {
        "city": "Guruvayoor",
        "value": 1
    },
    {
        "city": "Kanhangad",
        "value": 1
    },
    {
        "city": "Kannur",
        "value": 1
    },
    {
        "city": "Kasaragod",
        "value": 1
    },
    {
        "city": "Kayamkulam",
        "value": 1
    },
    {
        "city": "Kochi",
        "value": 1
    },
    {
        "city": "Kodungallur",
        "value": 1
    },
    {
        "city": "Kollam",
        "value": 1
    },
    {
        "city": "Kottayam",
        "value": 1
    },
    {
        "city": "Kozhikode",
        "value": 1
    },
    {
        "city": "Kunnamkulam",
        "value": 1
    },
    {
        "city": "Malappuram",
        "value": 1
    },
    {
        "city": "Mattannur",
        "value": 1
    },
    {
        "city": "Mavelikkara",
        "value": 1
    },
    {
        "city": "Mavoor",
        "value": 1
    },
    {
        "city": "Muvattupuzha",
        "value": 1
    },
    {
        "city": "Nedumangad",
        "value": 1
    },
    {
        "city": "Neyyattinkara",
        "value": 1
    },
    {
        "city": "Nilambur",
        "value": 1
    },
    {
        "city": "Ottappalam",
        "value": 1
    },
    {
        "city": "Palai",
        "value": 1
    },
    {
        "city": "Palakkad",
        "value": 1
    },
    {
        "city": "Panamattom",
        "value": 1
    },
    {
        "city": "Panniyannur",
        "value": 1
    },
    {
        "city": "Pappinisseri",
        "value": 1
    },
    {
        "city": "Paravoor",
        "value": 1
    },
    {
        "city": "Pathanamthitta",
        "value": 1
    },
    {
        "city": "Peringathur",
        "value": 1
    },
    {
        "city": "Perinthalmanna",
        "value": 1
    },
    {
        "city": "Perumbavoor",
        "value": 1
    },
    {
        "city": "Ponnani",
        "value": 1
    },
    {
        "city": "Punalur",
        "value": 1
    },
    {
        "city": "Puthuppally",
        "value": 1
    },
    {
        "city": "Koyilandy",
        "value": 1
    },
    {
        "city": "Shoranur",
        "value": 1
    },
    {
        "city": "Taliparamba",
        "value": 1
    },
    {
        "city": "Thiruvalla",
        "value": 1
    },
    {
        "city": "Thiruvananthapuram",
        "value": 1
    },
    {
        "city": "Thodupuzha",
        "value": 1
    },
    {
        "city": "Thrissur",
        "value": 1
    },
    {
        "city": "Tirur",
        "value": 1
    },
    {
        "city": "Vaikom",
        "value": 1
    },
    {
        "city": "Varkala",
        "value": 1
    },
    {
        "city": "Vatakara",
        "value": 1
    },
    {
        "city": "Alirajpur",
        "value": 1
    },
    {
        "city": "Ashok Nagar",
        "value": 1
    },
    {
        "city": "Balaghat",
        "value": 1
    },
    {
        "city": "Bhopal",
        "value": 1
    },
    {
        "city": "Ganjbasoda",
        "value": 1
    },
    {
        "city": "Gwalior",
        "value": 1
    },
    {
        "city": "Indore",
        "value": 1
    },
    {
        "city": "Itarsi",
        "value": 1
    },
    {
        "city": "Jabalpur",
        "value": 1
    },
    {
        "city": "Lahar",
        "value": 1
    },
    {
        "city": "Maharajpur",
        "value": 1
    },
    {
        "city": "Mahidpur",
        "value": 1
    },
    {
        "city": "Maihar",
        "value": 1
    },
    {
        "city": "Malaj Khand",
        "value": 1
    },
    {
        "city": "Manasa",
        "value": 1
    },
    {
        "city": "Manawar",
        "value": 1
    },
    {
        "city": "Mandideep",
        "value": 1
    },
    {
        "city": "Mandla",
        "value": 1
    },
    {
        "city": "Mandsaur",
        "value": 1
    },
    {
        "city": "Mauganj",
        "value": 1
    },
    {
        "city": "Mhow Cantonment",
        "value": 1
    },
    {
        "city": "Mhowgaon",
        "value": 1
    },
    {
        "city": "Morena",
        "value": 1
    },
    {
        "city": "Multai",
        "value": 1
    },
    {
        "city": "Mundi",
        "value": 1
    },
    {
        "city": "Murwara (Katni)",
        "value": 1
    },
    {
        "city": "Nagda",
        "value": 1
    },
    {
        "city": "Nainpur",
        "value": 1
    },
    {
        "city": "Narsinghgarh",
        "value": 1
    },
    {
        "city": "Neemuch",
        "value": 1
    },
    {
        "city": "Nepanagar",
        "value": 1
    },
    {
        "city": "Niwari",
        "value": 1
    },
    {
        "city": "Nowgong",
        "value": 1
    },
    {
        "city": "Nowrozabad (Khodargama)",
        "value": 1
    },
    {
        "city": "Pachore",
        "value": 1
    },
    {
        "city": "Pali",
        "value": 1
    },
    {
        "city": "Panagar",
        "value": 1
    },
    {
        "city": "Pandhurna",
        "value": 1
    },
    {
        "city": "Panna",
        "value": 1
    },
    {
        "city": "Pasan",
        "value": 1
    },
    {
        "city": "Pipariya",
        "value": 1
    },
    {
        "city": "Pithampur",
        "value": 1
    },
    {
        "city": "Porsa",
        "value": 1
    },
    {
        "city": "Prithvipur",
        "value": 1
    },
    {
        "city": "Raghogarh-Vijaypur",
        "value": 1
    },
    {
        "city": "Rahatgarh",
        "value": 1
    },
    {
        "city": "Raisen",
        "value": 1
    },
    {
        "city": "Rajgarh",
        "value": 1
    },
    {
        "city": "Ratlam",
        "value": 1
    },
    {
        "city": "Rau",
        "value": 1
    },
    {
        "city": "Rehli",
        "value": 1
    },
    {
        "city": "Rewa",
        "value": 1
    },
    {
        "city": "Sabalgarh",
        "value": 1
    },
    {
        "city": "Sagar",
        "value": 1
    },
    {
        "city": "Sanawad",
        "value": 1
    },
    {
        "city": "Sarangpur",
        "value": 1
    },
    {
        "city": "Sarni",
        "value": 1
    },
    {
        "city": "Satna",
        "value": 1
    },
    {
        "city": "Sausar",
        "value": 1
    },
    {
        "city": "Sehore",
        "value": 1
    },
    {
        "city": "Sendhwa",
        "value": 1
    },
    {
        "city": "Seoni",
        "value": 1
    },
    {
        "city": "Seoni-Malwa",
        "value": 1
    },
    {
        "city": "Shahdol",
        "value": 1
    },
    {
        "city": "Shajapur",
        "value": 1
    },
    {
        "city": "Shamgarh",
        "value": 1
    },
    {
        "city": "Sheopur",
        "value": 1
    },
    {
        "city": "Shivpuri",
        "value": 1
    },
    {
        "city": "Shujalpur",
        "value": 1
    },
    {
        "city": "Sidhi",
        "value": 1
    },
    {
        "city": "Sihora",
        "value": 1
    },
    {
        "city": "Singrauli",
        "value": 1
    },
    {
        "city": "Sironj",
        "value": 1
    },
    {
        "city": "Sohagpur",
        "value": 1
    },
    {
        "city": "Tarana",
        "value": 1
    },
    {
        "city": "Tikamgarh",
        "value": 1
    },
    {
        "city": "Ujjain",
        "value": 1
    },
    {
        "city": "Umaria",
        "value": 1
    },
    {
        "city": "Vidisha",
        "value": 1
    },
    {
        "city": "Vijaypur",
        "value": 1
    },
    {
        "city": "Wara Seoni",
        "value": 1
    },
    {
        "city": "[[]]",
        "value": 1
    },
    {
        "city": "Ahmednagar",
        "value": 1
    },
    {
        "city": "Akola",
        "value": 1
    },
    {
        "city": "Akot",
        "value": 1
    },
    {
        "city": "Amalner",
        "value": 1
    },
    {
        "city": "Ambejogai",
        "value": 1
    },
    {
        "city": "Amravati",
        "value": 1
    },
    {
        "city": "Anjangaon",
        "value": 1
    },
    {
        "city": "Arvi",
        "value": 1
    },
    {
        "city": "Bhiwandi",
        "value": 1
    },
    {
        "city": "Dhule",
        "value": 1
    },
    {
        "city": "Kalyan-Dombivali",
        "value": 1
    },
    {
        "city": "Ichalkaranji",
        "value": 1
    },
    {
        "city": "Karjat",
        "value": 1
    },
    {
        "city": "Latur",
        "value": 1
    },
    {
        "city": "Loha",
        "value": 1
    },
    {
        "city": "Lonar",
        "value": 1
    },
    {
        "city": "Lonavla",
        "value": 1
    },
    {
        "city": "Mahad",
        "value": 1
    },
    {
        "city": "Malegaon",
        "value": 1
    },
    {
        "city": "Malkapur",
        "value": 1
    },
    {
        "city": "Mangalvedhe",
        "value": 1
    },
    {
        "city": "Mangrulpir",
        "value": 1
    },
    {
        "city": "Manjlegaon",
        "value": 1
    },
    {
        "city": "Manmad",
        "value": 1
    },
    {
        "city": "Manwath",
        "value": 1
    },
    {
        "city": "Mehkar",
        "value": 1
    },
    {
        "city": "Mhaswad",
        "value": 1
    },
    {
        "city": "Mira-Bhayandar",
        "value": 1
    },
    {
        "city": "Morshi",
        "value": 1
    },
    {
        "city": "Mukhed",
        "value": 1
    },
    {
        "city": "Mul",
        "value": 1
    },
    {
        "city": "Greater Mumbai",
        "value": 1
    },
    {
        "city": "Murtijapur",
        "value": 1
    },
    {
        "city": "Nagpur",
        "value": 1
    },
    {
        "city": "Nanded-Waghala",
        "value": 1
    },
    {
        "city": "Nandgaon",
        "value": 1
    },
    {
        "city": "Nandura",
        "value": 1
    },
    {
        "city": "Nandurbar",
        "value": 1
    },
    {
        "city": "Narkhed",
        "value": 1
    },
    {
        "city": "Nashik",
        "value": 1
    },
    {
        "city": "Navi Mumbai",
        "value": 1
    },
    {
        "city": "Nawapur",
        "value": 1
    },
    {
        "city": "Nilanga",
        "value": 1
    },
    {
        "city": "Osmanabad",
        "value": 1
    },
    {
        "city": "Ozar",
        "value": 1
    },
    {
        "city": "Pachora",
        "value": 1
    },
    {
        "city": "Paithan",
        "value": 1
    },
    {
        "city": "Palghar",
        "value": 1
    },
    {
        "city": "Pandharkaoda",
        "value": 1
    },
    {
        "city": "Pandharpur",
        "value": 1
    },
    {
        "city": "Panvel",
        "value": 1
    },
    {
        "city": "Parbhani",
        "value": 1
    },
    {
        "city": "Parli",
        "value": 1
    },
    {
        "city": "Partur",
        "value": 1
    },
    {
        "city": "Pathardi",
        "value": 1
    },
    {
        "city": "Pathri",
        "value": 1
    },
    {
        "city": "Patur",
        "value": 1
    },
    {
        "city": "Pauni",
        "value": 1
    },
    {
        "city": "Pen",
        "value": 1
    },
    {
        "city": "Phaltan",
        "value": 1
    },
    {
        "city": "Pulgaon",
        "value": 1
    },
    {
        "city": "Pune",
        "value": 1
    },
    {
        "city": "Purna",
        "value": 1
    },
    {
        "city": "Pusad",
        "value": 1
    },
    {
        "city": "Rahuri",
        "value": 1
    },
    {
        "city": "Rajura",
        "value": 1
    },
    {
        "city": "Ramtek",
        "value": 1
    },
    {
        "city": "Ratnagiri",
        "value": 1
    },
    {
        "city": "Raver",
        "value": 1
    },
    {
        "city": "Risod",
        "value": 1
    },
    {
        "city": "Sailu",
        "value": 1
    },
    {
        "city": "Sangamner",
        "value": 1
    },
    {
        "city": "Sangli",
        "value": 1
    },
    {
        "city": "Sangole",
        "value": 1
    },
    {
        "city": "Sasvad",
        "value": 1
    },
    {
        "city": "Satana",
        "value": 1
    },
    {
        "city": "Satara",
        "value": 1
    },
    {
        "city": "Savner",
        "value": 1
    },
    {
        "city": "Sawantwadi",
        "value": 1
    },
    {
        "city": "Shahade",
        "value": 1
    },
    {
        "city": "Shegaon",
        "value": 1
    },
    {
        "city": "Shendurjana",
        "value": 1
    },
    {
        "city": "Shirdi",
        "value": 1
    },
    {
        "city": "Shirpur-Warwade",
        "value": 1
    },
    {
        "city": "Shirur",
        "value": 1
    },
    {
        "city": "Shrigonda",
        "value": 1
    },
    {
        "city": "Shrirampur",
        "value": 1
    },
    {
        "city": "Sillod",
        "value": 1
    },
    {
        "city": "Sinnar",
        "value": 1
    },
    {
        "city": "Solapur",
        "value": 1
    },
    {
        "city": "Soyagaon",
        "value": 1
    },
    {
        "city": "Talegaon Dabhade",
        "value": 1
    },
    {
        "city": "Talode",
        "value": 1
    },
    {
        "city": "Tasgaon",
        "value": 1
    },
    {
        "city": "Thane",
        "value": 1
    },
    {
        "city": "Tirora",
        "value": 1
    },
    {
        "city": "Tuljapur",
        "value": 1
    },
    {
        "city": "Tumsar",
        "value": 1
    },
    {
        "city": "Uchgaon",
        "value": 1
    },
    {
        "city": "Udgir",
        "value": 1
    },
    {
        "city": "Umarga",
        "value": 1
    },
    {
        "city": "Umarkhed",
        "value": 1
    },
    {
        "city": "Umred",
        "value": 1
    },
    {
        "city": "Uran",
        "value": 1
    },
    {
        "city": "Uran Islampur",
        "value": 1
    },
    {
        "city": "Vadgaon Kasba",
        "value": 1
    },
    {
        "city": "Vaijapur",
        "value": 1
    },
    {
        "city": "Vasai-Virar",
        "value": 1
    },
    {
        "city": "Vita",
        "value": 1
    },
    {
        "city": "Wadgaon Road",
        "value": 1
    },
    {
        "city": "Wai",
        "value": 1
    },
    {
        "city": "Wani",
        "value": 1
    },
    {
        "city": "Wardha",
        "value": 1
    },
    {
        "city": "Warora",
        "value": 1
    },
    {
        "city": "Warud",
        "value": 1
    },
    {
        "city": "Washim",
        "value": 1
    },
    {
        "city": "Yavatmal",
        "value": 1
    },
    {
        "city": "Yawal",
        "value": 1
    },
    {
        "city": "Yevla",
        "value": 1
    },
    {
        "city": "Imphal",
        "value": 1
    },
    {
        "city": "Lilong",
        "value": 1
    },
    {
        "city": "Mayang Imphal",
        "value": 1
    },
    {
        "city": "Thoubal",
        "value": 1
    },
    {
        "city": "Nongstoin",
        "value": 1
    },
    {
        "city": "Shillong",
        "value": 1
    },
    {
        "city": "Tura",
        "value": 1
    },
    {
        "city": "Aizawl",
        "value": 1
    },
    {
        "city": "Lunglei",
        "value": 1
    },
    {
        "city": "Saiha",
        "value": 1
    },
    {
        "city": "Dimapur",
        "value": 1
    },
    {
        "city": "Kohima",
        "value": 1
    },
    {
        "city": "Mokokchung",
        "value": 1
    },
    {
        "city": "Tuensang",
        "value": 1
    },
    {
        "city": "Wokha",
        "value": 1
    },
    {
        "city": "Zunheboto",
        "value": 1
    },
    {
        "city": "Balangir",
        "value": 1
    },
    {
        "city": "Baleshwar Town",
        "value": 1
    },
    {
        "city": "Barbil",
        "value": 1
    },
    {
        "city": "Bargarh",
        "value": 1
    },
    {
        "city": "Baripada Town",
        "value": 1
    },
    {
        "city": "Bhadrak",
        "value": 1
    },
    {
        "city": "Bhawanipatna",
        "value": 1
    },
    {
        "city": "Bhubaneswar",
        "value": 1
    },
    {
        "city": "Brahmapur",
        "value": 1
    },
    {
        "city": "Byasanagar",
        "value": 1
    },
    {
        "city": "Cuttack",
        "value": 1
    },
    {
        "city": "Dhenkanal",
        "value": 1
    },
    {
        "city": "Jatani",
        "value": 1
    },
    {
        "city": "Jharsuguda",
        "value": 1
    },
    {
        "city": "Kendrapara",
        "value": 1
    },
    {
        "city": "Kendujhar",
        "value": 1
    },
    {
        "city": "Malkangiri",
        "value": 1
    },
    {
        "city": "Nabarangapur",
        "value": 1
    },
    {
        "city": "Paradip",
        "value": 1
    },
    {
        "city": "Parlakhemundi",
        "value": 1
    },
    {
        "city": "Pattamundai",
        "value": 1
    },
    {
        "city": "Phulabani",
        "value": 1
    },
    {
        "city": "Puri",
        "value": 1
    },
    {
        "city": "Rairangpur",
        "value": 1
    },
    {
        "city": "Rajagangapur",
        "value": 1
    },
    {
        "city": "Raurkela",
        "value": 1
    },
    {
        "city": "Rayagada",
        "value": 1
    },
    {
        "city": "Sambalpur",
        "value": 1
    },
    {
        "city": "Soro",
        "value": 1
    },
    {
        "city": "Sunabeda",
        "value": 1
    },
    {
        "city": "Sundargarh",
        "value": 1
    },
    {
        "city": "Talcher",
        "value": 1
    },
    {
        "city": "Tarbha",
        "value": 1
    },
    {
        "city": "Titlagarh",
        "value": 1
    },
    {
        "city": "Karaikal",
        "value": 1
    },
    {
        "city": "Mahe",
        "value": 1
    },
    {
        "city": "Pondicherry",
        "value": 1
    },
    {
        "city": "Yanam",
        "value": 1
    },
    {
        "city": "Amritsar",
        "value": 1
    },
    {
        "city": "Barnala",
        "value": 1
    },
    {
        "city": "Batala",
        "value": 1
    },
    {
        "city": "Bathinda",
        "value": 1
    },
    {
        "city": "Dhuri",
        "value": 1
    },
    {
        "city": "Faridkot",
        "value": 1
    },
    {
        "city": "Fazilka",
        "value": 1
    },
    {
        "city": "Firozpur",
        "value": 1
    },
    {
        "city": "Firozpur Cantt.",
        "value": 1
    },
    {
        "city": "Gobindgarh",
        "value": 1
    },
    {
        "city": "Gurdaspur",
        "value": 1
    },
    {
        "city": "Hoshiarpur",
        "value": 1
    },
    {
        "city": "Jagraon",
        "value": 1
    },
    {
        "city": "Jalandhar Cantt.",
        "value": 1
    },
    {
        "city": "Jalandhar",
        "value": 1
    },
    {
        "city": "Kapurthala",
        "value": 1
    },
    {
        "city": "Khanna",
        "value": 1
    },
    {
        "city": "Kharar",
        "value": 1
    },
    {
        "city": "Kot Kapura",
        "value": 1
    },
    {
        "city": "Longowal",
        "value": 1
    },
    {
        "city": "Ludhiana",
        "value": 1
    },
    {
        "city": "Malerkotla",
        "value": 1
    },
    {
        "city": "Malout",
        "value": 1
    },
    {
        "city": "Moga",
        "value": 1
    },
    {
        "city": "Mohali",
        "value": 1
    },
    {
        "city": "Morinda, India",
        "value": 1
    },
    {
        "city": "Mukerian",
        "value": 1
    },
    {
        "city": "Muktsar",
        "value": 1
    },
    {
        "city": "Nabha",
        "value": 1
    },
    {
        "city": "Nakodar",
        "value": 1
    },
    {
        "city": "Nangal",
        "value": 1
    },
    {
        "city": "Nawanshahr",
        "value": 1
    },
    {
        "city": "Pathankot",
        "value": 1
    },
    {
        "city": "Patiala",
        "value": 1
    },
    {
        "city": "Pattran",
        "value": 1
    },
    {
        "city": "Patti",
        "value": 1
    },
    {
        "city": "Phagwara",
        "value": 1
    },
    {
        "city": "Phillaur",
        "value": 1
    },
    {
        "city": "Qadian",
        "value": 1
    },
    {
        "city": "Raikot",
        "value": 1
    },
    {
        "city": "Rajpura",
        "value": 1
    },
    {
        "city": "Rampura Phul",
        "value": 1
    },
    {
        "city": "Rupnagar",
        "value": 1
    },
    {
        "city": "Samana",
        "value": 1
    },
    {
        "city": "Sangrur",
        "value": 1
    },
    {
        "city": "Sirhind Fatehgarh Sahib",
        "value": 1
    },
    {
        "city": "Sujanpur",
        "value": 1
    },
    {
        "city": "Sunam",
        "value": 1
    },
    {
        "city": "Talwara",
        "value": 1
    },
    {
        "city": "Tarn Taran",
        "value": 1
    },
    {
        "city": "Urmar Tanda",
        "value": 1
    },
    {
        "city": "Zira",
        "value": 1
    },
    {
        "city": "Zirakpur",
        "value": 1
    },
    {
        "city": "Ajmer",
        "value": 1
    },
    {
        "city": "Alwar",
        "value": 1
    },
    {
        "city": "Bikaner",
        "value": 1
    },
    {
        "city": "Bharatpur",
        "value": 1
    },
    {
        "city": "Bhilwara",
        "value": 1
    },
    {
        "city": "Jaipur",
        "value": 1
    },
    {
        "city": "Jodhpur",
        "value": 1
    },
    {
        "city": "Lachhmangarh",
        "value": 1
    },
    {
        "city": "Ladnu",
        "value": 1
    },
    {
        "city": "Lakheri",
        "value": 1
    },
    {
        "city": "Lalsot",
        "value": 1
    },
    {
        "city": "Losal",
        "value": 1
    },
    {
        "city": "Makrana",
        "value": 1
    },
    {
        "city": "Malpura",
        "value": 1
    },
    {
        "city": "Mandalgarh",
        "value": 1
    },
    {
        "city": "Mandawa",
        "value": 1
    },
    {
        "city": "Merta City",
        "value": 1
    },
    {
        "city": "Mount Abu",
        "value": 1
    },
    {
        "city": "Nadbai",
        "value": 1
    },
    {
        "city": "Nagar",
        "value": 1
    },
    {
        "city": "Nagaur",
        "value": 1
    },
    {
        "city": "Nasirabad",
        "value": 1
    },
    {
        "city": "Nathdwara",
        "value": 1
    },
    {
        "city": "Neem-Ka-Thana",
        "value": 1
    },
    {
        "city": "Nimbahera",
        "value": 1
    },
    {
        "city": "Nohar",
        "value": 1
    },
    {
        "city": "Phalodi",
        "value": 1
    },
    {
        "city": "Phulera",
        "value": 1
    },
    {
        "city": "Pilani",
        "value": 1
    },
    {
        "city": "Pilibanga",
        "value": 1
    },
    {
        "city": "Pindwara",
        "value": 1
    },
    {
        "city": "Pipar City",
        "value": 1
    },
    {
        "city": "Prantij",
        "value": 1
    },
    {
        "city": "Pratapgarh",
        "value": 1
    },
    {
        "city": "Raisinghnagar",
        "value": 1
    },
    {
        "city": "Rajakhera",
        "value": 1
    },
    {
        "city": "Rajaldesar",
        "value": 1
    },
    {
        "city": "Rajgarh (Alwar)",
        "value": 1
    },
    {
        "city": "Rajgarh (Churu)",
        "value": 1
    },
    {
        "city": "Rajsamand",
        "value": 1
    },
    {
        "city": "Ramganj Mandi",
        "value": 1
    },
    {
        "city": "Ramngarh",
        "value": 1
    },
    {
        "city": "Ratangarh",
        "value": 1
    },
    {
        "city": "Rawatbhata",
        "value": 1
    },
    {
        "city": "Rawatsar",
        "value": 1
    },
    {
        "city": "Reengus",
        "value": 1
    },
    {
        "city": "Sadri",
        "value": 1
    },
    {
        "city": "Sadulshahar",
        "value": 1
    },
    {
        "city": "Sadulpur",
        "value": 1
    },
    {
        "city": "Sagwara",
        "value": 1
    },
    {
        "city": "Sambhar",
        "value": 1
    },
    {
        "city": "Sanchore",
        "value": 1
    },
    {
        "city": "Sangaria",
        "value": 1
    },
    {
        "city": "Sardarshahar",
        "value": 1
    },
    {
        "city": "Sawai Madhopur",
        "value": 1
    },
    {
        "city": "Shahpura",
        "value": 1
    },
    {
        "city": "Sheoganj",
        "value": 1
    },
    {
        "city": "Sikar",
        "value": 1
    },
    {
        "city": "Sirohi",
        "value": 1
    },
    {
        "city": "Sojat",
        "value": 1
    },
    {
        "city": "Sri Madhopur",
        "value": 1
    },
    {
        "city": "Sujangarh",
        "value": 1
    },
    {
        "city": "Sumerpur",
        "value": 1
    },
    {
        "city": "Suratgarh",
        "value": 1
    },
    {
        "city": "Taranagar",
        "value": 1
    },
    {
        "city": "Todabhim",
        "value": 1
    },
    {
        "city": "Todaraisingh",
        "value": 1
    },
    {
        "city": "Tonk",
        "value": 1
    },
    {
        "city": "Udaipur",
        "value": 1
    },
    {
        "city": "Udaipurwati",
        "value": 1
    },
    {
        "city": "Vijainagar, Ajmer",
        "value": 1
    },
    {
        "city": "Arakkonam",
        "value": 1
    },
    {
        "city": "Aruppukkottai",
        "value": 1
    },
    {
        "city": "Chennai",
        "value": 1
    },
    {
        "city": "Coimbatore",
        "value": 1
    },
    {
        "city": "Erode",
        "value": 1
    },
    {
        "city": "Gobichettipalayam",
        "value": 1
    },
    {
        "city": "Kancheepuram",
        "value": 1
    },
    {
        "city": "Karur",
        "value": 1
    },
    {
        "city": "Lalgudi",
        "value": 1
    },
    {
        "city": "Madurai",
        "value": 1
    },
    {
        "city": "Manachanallur",
        "value": 1
    },
    {
        "city": "Nagapattinam",
        "value": 1
    },
    {
        "city": "Nagercoil",
        "value": 1
    },
    {
        "city": "Namagiripettai",
        "value": 1
    },
    {
        "city": "Namakkal",
        "value": 1
    },
    {
        "city": "Nandivaram-Guduvancheri",
        "value": 1
    },
    {
        "city": "Nanjikottai",
        "value": 1
    },
    {
        "city": "Natham",
        "value": 1
    },
    {
        "city": "Nellikuppam",
        "value": 1
    },
    {
        "city": "Neyveli (TS)",
        "value": 1
    },
    {
        "city": "O' Valley",
        "value": 1
    },
    {
        "city": "Oddanchatram",
        "value": 1
    },
    {
        "city": "P.N.Patti",
        "value": 1
    },
    {
        "city": "Pacode",
        "value": 1
    },
    {
        "city": "Padmanabhapuram",
        "value": 1
    },
    {
        "city": "Palani",
        "value": 1
    },
    {
        "city": "Palladam",
        "value": 1
    },
    {
        "city": "Pallapatti",
        "value": 1
    },
    {
        "city": "Pallikonda",
        "value": 1
    },
    {
        "city": "Panagudi",
        "value": 1
    },
    {
        "city": "Panruti",
        "value": 1
    },
    {
        "city": "Paramakudi",
        "value": 1
    },
    {
        "city": "Parangipettai",
        "value": 1
    },
    {
        "city": "Pattukkottai",
        "value": 1
    },
    {
        "city": "Perambalur",
        "value": 1
    },
    {
        "city": "Peravurani",
        "value": 1
    },
    {
        "city": "Periyakulam",
        "value": 1
    },
    {
        "city": "Periyasemur",
        "value": 1
    },
    {
        "city": "Pernampattu",
        "value": 1
    },
    {
        "city": "Pollachi",
        "value": 1
    },
    {
        "city": "Polur",
        "value": 1
    },
    {
        "city": "Ponneri",
        "value": 1
    },
    {
        "city": "Pudukkottai",
        "value": 1
    },
    {
        "city": "Pudupattinam",
        "value": 1
    },
    {
        "city": "Puliyankudi",
        "value": 1
    },
    {
        "city": "Punjaipugalur",
        "value": 1
    },
    {
        "city": "Ranipet",
        "value": 1
    },
    {
        "city": "Rajapalayam",
        "value": 1
    },
    {
        "city": "Ramanathapuram",
        "value": 1
    },
    {
        "city": "Rameshwaram",
        "value": 1
    },
    {
        "city": "Rasipuram",
        "value": 1
    },
    {
        "city": "Salem",
        "value": 1
    },
    {
        "city": "Sankarankoil",
        "value": 1
    },
    {
        "city": "Sankari",
        "value": 1
    },
    {
        "city": "Sathyamangalam",
        "value": 1
    },
    {
        "city": "Sattur",
        "value": 1
    },
    {
        "city": "Shenkottai",
        "value": 1
    },
    {
        "city": "Sholavandan",
        "value": 1
    },
    {
        "city": "Sholingur",
        "value": 1
    },
    {
        "city": "Sirkali",
        "value": 1
    },
    {
        "city": "Sivaganga",
        "value": 1
    },
    {
        "city": "Sivagiri",
        "value": 1
    },
    {
        "city": "Sivakasi",
        "value": 1
    },
    {
        "city": "Srivilliputhur",
        "value": 1
    },
    {
        "city": "Surandai",
        "value": 1
    },
    {
        "city": "Suriyampalayam",
        "value": 1
    },
    {
        "city": "Tenkasi",
        "value": 1
    },
    {
        "city": "Thammampatti",
        "value": 1
    },
    {
        "city": "Thanjavur",
        "value": 1
    },
    {
        "city": "Tharamangalam",
        "value": 1
    },
    {
        "city": "Tharangambadi",
        "value": 1
    },
    {
        "city": "Theni Allinagaram",
        "value": 1
    },
    {
        "city": "Thirumangalam",
        "value": 1
    },
    {
        "city": "Thirupuvanam",
        "value": 1
    },
    {
        "city": "Thiruthuraipoondi",
        "value": 1
    },
    {
        "city": "Thiruvallur",
        "value": 1
    },
    {
        "city": "Thiruvarur",
        "value": 1
    },
    {
        "city": "Thuraiyur",
        "value": 1
    },
    {
        "city": "Tindivanam",
        "value": 1
    },
    {
        "city": "Tiruchendur",
        "value": 1
    },
    {
        "city": "Tiruchengode",
        "value": 1
    },
    {
        "city": "Tiruchirappalli",
        "value": 1
    },
    {
        "city": "Tirukalukundram",
        "value": 1
    },
    {
        "city": "Tirukkoyilur",
        "value": 1
    },
    {
        "city": "Tirunelveli",
        "value": 1
    },
    {
        "city": "Tirupathur",
        "value": 1
    },
    {
        "city": "Tiruppur",
        "value": 1
    },
    {
        "city": "Tiruttani",
        "value": 1
    },
    {
        "city": "Tiruvannamalai",
        "value": 1
    },
    {
        "city": "Tiruvethipuram",
        "value": 1
    },
    {
        "city": "Tittakudi",
        "value": 1
    },
    {
        "city": "Udhagamandalam",
        "value": 1
    },
    {
        "city": "Udumalaipettai",
        "value": 1
    },
    {
        "city": "Unnamalaikadai",
        "value": 1
    },
    {
        "city": "Usilampatti",
        "value": 1
    },
    {
        "city": "Uthamapalayam",
        "value": 1
    },
    {
        "city": "Uthiramerur",
        "value": 1
    },
    {
        "city": "Vadakkuvalliyur",
        "value": 1
    },
    {
        "city": "Vadalur",
        "value": 1
    },
    {
        "city": "Vadipatti",
        "value": 1
    },
    {
        "city": "Valparai",
        "value": 1
    },
    {
        "city": "Vandavasi",
        "value": 1
    },
    {
        "city": "Vaniyambadi",
        "value": 1
    },
    {
        "city": "Vedaranyam",
        "value": 1
    },
    {
        "city": "Vellakoil",
        "value": 1
    },
    {
        "city": "Vellore",
        "value": 1
    },
    {
        "city": "Vikramasingapuram",
        "value": 1
    },
    {
        "city": "Viluppuram",
        "value": 1
    },
    {
        "city": "Virudhachalam",
        "value": 1
    },
    {
        "city": "Virudhunagar",
        "value": 1
    },
    {
        "city": "Viswanatham",
        "value": 1
    },
    {
        "city": "Adilabad",
        "value": 1
    },
    {
        "city": "Bellampalle",
        "value": 1
    },
    {
        "city": "Bhadrachalam",
        "value": 1
    },
    {
        "city": "Bhainsa",
        "value": 1
    },
    {
        "city": "Bhongir",
        "value": 1
    },
    {
        "city": "Bodhan",
        "value": 1
    },
    {
        "city": "Farooqnagar",
        "value": 1
    },
    {
        "city": "Gadwal",
        "value": 1
    },
    {
        "city": "Hyderabad",
        "value": 1
    },
    {
        "city": "Jagtial",
        "value": 1
    },
    {
        "city": "Jangaon",
        "value": 1
    },
    {
        "city": "Kagaznagar",
        "value": 1
    },
    {
        "city": "Kamareddy",
        "value": 1
    },
    {
        "city": "Karimnagar",
        "value": 1
    },
    {
        "city": "Khammam",
        "value": 1
    },
    {
        "city": "Koratla",
        "value": 1
    },
    {
        "city": "Kothagudem",
        "value": 1
    },
    {
        "city": "Kyathampalle",
        "value": 1
    },
    {
        "city": "Mahbubnagar",
        "value": 1
    },
    {
        "city": "Mancherial",
        "value": 1
    },
    {
        "city": "Mandamarri",
        "value": 1
    },
    {
        "city": "Manuguru",
        "value": 1
    },
    {
        "city": "Medak",
        "value": 1
    },
    {
        "city": "Miryalaguda",
        "value": 1
    },
    {
        "city": "Nagarkurnool",
        "value": 1
    },
    {
        "city": "Narayanpet",
        "value": 1
    },
    {
        "city": "Nirmal",
        "value": 1
    },
    {
        "city": "Nizamabad",
        "value": 1
    },
    {
        "city": "Palwancha",
        "value": 1
    },
    {
        "city": "Ramagundam",
        "value": 1
    },
    {
        "city": "Sadasivpet",
        "value": 1
    },
    {
        "city": "Sangareddy",
        "value": 1
    },
    {
        "city": "Siddipet",
        "value": 1
    },
    {
        "city": "Sircilla",
        "value": 1
    },
    {
        "city": "Suryapet",
        "value": 1
    },
    {
        "city": "Tandur",
        "value": 1
    },
    {
        "city": "Vikarabad",
        "value": 1
    },
    {
        "city": "Wanaparthy",
        "value": 1
    },
    {
        "city": "Warangal",
        "value": 1
    },
    {
        "city": "Yellandu",
        "value": 1
    },
    {
        "city": "Agartala",
        "value": 1
    },
    {
        "city": "Belonia",
        "value": 1
    },
    {
        "city": "Dharmanagar",
        "value": 1
    },
    {
        "city": "Kailasahar",
        "value": 1
    },
    {
        "city": "Khowai",
        "value": 1
    },
    {
        "city": "Achhnera",
        "value": 1
    },
    {
        "city": "Agra",
        "value": 1
    },
    {
        "city": "Aligarh",
        "value": 1
    },
    {
        "city": "Allahabad",
        "value": 1
    },
    {
        "city": "Amroha",
        "value": 1
    },
    {
        "city": "Azamgarh",
        "value": 1
    },
    {
        "city": "Bahraich",
        "value": 1
    },
    {
        "city": "Chandausi",
        "value": 1
    },
    {
        "city": "Etawah",
        "value": 1
    },
    {
        "city": "Firozabad",
        "value": 1
    },
    {
        "city": "Fatehpur Sikri",
        "value": 1
    },
    {
        "city": "Hapur",
        "value": 1
    },
    {
        "city": "Hardoi ",
        "value": 1
    },
    {
        "city": "Jhansi",
        "value": 1
    },
    {
        "city": "Kalpi",
        "value": 1
    },
    {
        "city": "Kanpur",
        "value": 1
    },
    {
        "city": "Khair",
        "value": 1
    },
    {
        "city": "Laharpur",
        "value": 1
    },
    {
        "city": "Lakhimpur",
        "value": 1
    },
    {
        "city": "Lal Gopalganj Nindaura",
        "value": 1
    },
    {
        "city": "Lalitpur",
        "value": 1
    },
    {
        "city": "Lar",
        "value": 1
    },
    {
        "city": "Loni",
        "value": 1
    },
    {
        "city": "Lucknow",
        "value": 1
    },
    {
        "city": "Mathura",
        "value": 1
    },
    {
        "city": "Meerut",
        "value": 1
    },
    {
        "city": "Modinagar",
        "value": 1
    },
    {
        "city": "Moradabad",
        "value": 1
    },
    {
        "city": "Nagina",
        "value": 1
    },
    {
        "city": "Najibabad",
        "value": 1
    },
    {
        "city": "Nakur",
        "value": 1
    },
    {
        "city": "Nanpara",
        "value": 1
    },
    {
        "city": "Naraura",
        "value": 1
    },
    {
        "city": "Naugawan Sadat",
        "value": 1
    },
    {
        "city": "Nautanwa",
        "value": 1
    },
    {
        "city": "Nawabganj",
        "value": 1
    },
    {
        "city": "Nehtaur",
        "value": 1
    },
    {
        "city": "Niwai",
        "value": 1
    },
    {
        "city": "Noida",
        "value": 1
    },
    {
        "city": "Noorpur",
        "value": 1
    },
    {
        "city": "Obra",
        "value": 1
    },
    {
        "city": "Orai",
        "value": 1
    },
    {
        "city": "Padrauna",
        "value": 1
    },
    {
        "city": "Palia Kalan",
        "value": 1
    },
    {
        "city": "Parasi",
        "value": 1
    },
    {
        "city": "Phulpur",
        "value": 1
    },
    {
        "city": "Pihani",
        "value": 1
    },
    {
        "city": "Pilibhit",
        "value": 1
    },
    {
        "city": "Pilkhuwa",
        "value": 1
    },
    {
        "city": "Powayan",
        "value": 1
    },
    {
        "city": "Pukhrayan",
        "value": 1
    },
    {
        "city": "Puranpur",
        "value": 1
    },
    {
        "city": "Purquazi",
        "value": 1
    },
    {
        "city": "Purwa",
        "value": 1
    },
    {
        "city": "Rae Bareli",
        "value": 1
    },
    {
        "city": "Rampur",
        "value": 1
    },
    {
        "city": "Rampur Maniharan",
        "value": 1
    },
    {
        "city": "Rasra",
        "value": 1
    },
    {
        "city": "Rath",
        "value": 1
    },
    {
        "city": "Renukoot",
        "value": 1
    },
    {
        "city": "Reoti",
        "value": 1
    },
    {
        "city": "Robertsganj",
        "value": 1
    },
    {
        "city": "Rudauli",
        "value": 1
    },
    {
        "city": "Rudrapur",
        "value": 1
    },
    {
        "city": "Sadabad",
        "value": 1
    },
    {
        "city": "Safipur",
        "value": 1
    },
    {
        "city": "Saharanpur",
        "value": 1
    },
    {
        "city": "Sahaspur",
        "value": 1
    },
    {
        "city": "Sahaswan",
        "value": 1
    },
    {
        "city": "Sahawar",
        "value": 1
    },
    {
        "city": "Sahjanwa",
        "value": 1
    },
    {
        "city": "Saidpur",
        "value": 1
    },
    {
        "city": "Sambhal",
        "value": 1
    },
    {
        "city": "Samdhan",
        "value": 1
    },
    {
        "city": "Samthar",
        "value": 1
    },
    {
        "city": "Sandi",
        "value": 1
    },
    {
        "city": "Sandila",
        "value": 1
    },
    {
        "city": "Sardhana",
        "value": 1
    },
    {
        "city": "Seohara",
        "value": 1
    },
    {
        "city": "Shahabad, Hardoi",
        "value": 1
    },
    {
        "city": "Shahabad, Rampur",
        "value": 1
    },
    {
        "city": "Shahganj",
        "value": 1
    },
    {
        "city": "Shahjahanpur",
        "value": 1
    },
    {
        "city": "Shamli",
        "value": 1
    },
    {
        "city": "Shamsabad, Agra",
        "value": 1
    },
    {
        "city": "Shamsabad, Farrukhabad",
        "value": 1
    },
    {
        "city": "Sherkot",
        "value": 1
    },
    {
        "city": "Shikarpur, Bulandshahr",
        "value": 1
    },
    {
        "city": "Shikohabad",
        "value": 1
    },
    {
        "city": "Shishgarh",
        "value": 1
    },
    {
        "city": "Siana",
        "value": 1
    },
    {
        "city": "Sikanderpur",
        "value": 1
    },
    {
        "city": "Sikandra Rao",
        "value": 1
    },
    {
        "city": "Sikandrabad",
        "value": 1
    },
    {
        "city": "Sirsaganj",
        "value": 1
    },
    {
        "city": "Sitapur",
        "value": 1
    },
    {
        "city": "Soron",
        "value": 1
    },
    {
        "city": "Suar",
        "value": 1
    },
    {
        "city": "Sultanpur",
        "value": 1
    },
    {
        "city": "Tanda",
        "value": 1
    },
    {
        "city": "Thakurdwara",
        "value": 1
    },
    {
        "city": "Thana Bhawan",
        "value": 1
    },
    {
        "city": "Tilhar",
        "value": 1
    },
    {
        "city": "Tirwaganj",
        "value": 1
    },
    {
        "city": "Tulsipur",
        "value": 1
    },
    {
        "city": "Tundla",
        "value": 1
    },
    {
        "city": "Ujhani",
        "value": 1
    },
    {
        "city": "Unnao",
        "value": 1
    },
    {
        "city": "Utraula",
        "value": 1
    },
    {
        "city": "Varanasi",
        "value": 1
    },
    {
        "city": "Vrindavan",
        "value": 1
    },
    {
        "city": "Warhapur",
        "value": 1
    },
    {
        "city": "Zaidpur",
        "value": 1
    },
    {
        "city": "Zamania",
        "value": 1
    },
    {
        "city": "Bageshwar",
        "value": 1
    },
    {
        "city": "Dehradun",
        "value": 1
    },
    {
        "city": "Haldwani-cum-Kathgodam",
        "value": 1
    },
    {
        "city": "Hardwar",
        "value": 1
    },
    {
        "city": "Kashipur",
        "value": 1
    },
    {
        "city": "Manglaur",
        "value": 1
    },
    {
        "city": "Mussoorie",
        "value": 1
    },
    {
        "city": "Nagla",
        "value": 1
    },
    {
        "city": "Nainital",
        "value": 1
    },
    {
        "city": "Pauri",
        "value": 1
    },
    {
        "city": "Pithoragarh",
        "value": 1
    },
    {
        "city": "Rishikesh",
        "value": 1
    },
    {
        "city": "Roorkee",
        "value": 1
    },
    {
        "city": "Sitarganj",
        "value": 1
    },
    {
        "city": "Srinagar",
        "value": 1
    },
    {
        "city": "Tehri",
        "value": 1
    },
    {
        "city": "Adra",
        "value": 1
    },
    {
        "city": "Alipurduar",
        "value": 1
    },
    {
        "city": "Arambagh",
        "value": 1
    },
    {
        "city": "Asansol",
        "value": 1
    },
    {
        "city": "Baharampur",
        "value": 1
    },
    {
        "city": "Balurghat",
        "value": 1
    },
    {
        "city": "Bankura",
        "value": 1
    },
    {
        "city": "Darjiling",
        "value": 1
    },
    {
        "city": "English Bazar",
        "value": 1
    },
    {
        "city": "Gangarampur",
        "value": 1
    },
    {
        "city": "Habra",
        "value": 1
    },
    {
        "city": "Hugli-Chinsurah",
        "value": 1
    },
    {
        "city": "Jalpaiguri",
        "value": 1
    },
    {
        "city": "Jhargram",
        "value": 1
    },
    {
        "city": "Kalimpong",
        "value": 1
    },
    {
        "city": "Kharagpur",
        "value": 1
    },
    {
        "city": "Kolkata",
        "value": 1
    },
    {
        "city": "Mainaguri",
        "value": 1
    },
    {
        "city": "Malda",
        "value": 1
    },
    {
        "city": "Mathabhanga",
        "value": 1
    },
    {
        "city": "Medinipur",
        "value": 1
    },
    {
        "city": "Memari",
        "value": 1
    },
    {
        "city": "Monoharpur",
        "value": 1
    },
    {
        "city": "Murshidabad",
        "value": 1
    },
    {
        "city": "Nabadwip",
        "value": 1
    },
    {
        "city": "Naihati",
        "value": 1
    },
    {
        "city": "Panchla",
        "value": 1
    },
    {
        "city": "Pandua",
        "value": 1
    },
    {
        "city": "Paschim Punropara",
        "value": 1
    },
    {
        "city": "Purulia",
        "value": 1
    },
    {
        "city": "Raghunathpur",
        "value": 1
    },
    {
        "city": "Raghunathganj",
        "value": 1
    },
    {
        "city": "Raiganj",
        "value": 1
    },
    {
        "city": "Rampurhat",
        "value": 1
    },
    {
        "city": "Ranaghat",
        "value": 1
    },
    {
        "city": "Sainthia",
        "value": 1
    },
    {
        "city": "Santipur",
        "value": 1
    },
    {
        "city": "Siliguri",
        "value": 1
    },
    {
        "city": "Sonamukhi",
        "value": 1
    },
    {
        "city": "Srirampore",
        "value": 1
    },
    {
        "city": "Suri",
        "value": 1
    },
    {
        "city": "Taki",
        "value": 1
    },
    {
        "city": "Tamluk",
        "value": 1
    },
    {
        "city": "Tarakeswar",
        "value": 1
    }
]
for i in l:
    data.insert(i)
for ele in data.find():
    pprint(ele)