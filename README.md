# Acu-CPGs

The Acu-CPGs dataset is organized into two files within the `data` directory, `ZH_CPGs.xlsx` and `EN_CPGs.xlsx`, which contain the Chinese and English versions of the acupuncture guideline recommendations, respectively. Each record within the dataset is structured according to the PICO (Patient/Population, Intervention, Comparison, Outcome) framework and comprises 16 distinct items: Publication year, Issuing Organization, Guidelines Title, Western Medicine Diagnosis, TCM Diagnosis, Pattern Diagnosis, Patient/Population, Intervention, Acupoint Prescription, Commonly Used Medicine, Acupuncture Technique, Treatment Course, Precautions, Comparisons, Outcome Measures, and Recommendations.

## Directory Structure

See [directory.html](directory.html) for a visual overview, or refer to the structure below:

```
Acu-CPGs/
├── README.md
├── LICENSE
├── data/
│   ├── ZH_CPGs.xlsx        # acupuncture guidelines (Chinese Version)
│   └── EN_CPGs.xlsx        # acupuncture guidelines (English Version)
└── code/
    ├── main.py
    ├── baselib.py
    ├── excel_2_sqlite.py
    ├── merge_excel.py
    ├── translate.py
    ├── sql_hit.py
    ├── llms_test.py
    ├── text2sql_test.py
    ├── requirements.txt
    ├── readme.md
    ├── prompt/
    │   ├── structured prompt.docx
    │   └── glossary.doc
    └── dst_data/
        └── Case score.xlsx
```

## License

This dataset is licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
