from src.visualization import Chart1_Use_of_imprisonment_PFAs as chart1
from src.visualization import Chart2_PFA_Offences as chart2
from src.visualization import Chart3_Sentence_Type as chart3

if __name__ == "__main__":
    chart1.make_pfa_sentence_length_charts(chart1.filename, chart1.folder)
    chart2
    chart3