# Excel File Analysis Report

File: דירה להשקעה עדכון  V3.2 8.24.xlsx
Total Sheets: 6

## Sheet: Data Table

- **Dimensions:** 56 rows × 28 columns
- **Purpose:** (See analysis below)

### Column Names:
1. ID
2. לינק
3. עיר
4. שכונה
5. רחוב
6. מצב הדירה
7. חדשה מקבלן?
8. דירוג מצב הדירה
9. גודל דירה (מר)
10. מספר חדרים
11. קומה
12. מעלית
13. גודל מרפסת (מר)
14. ממד
15. חניה
16. פינוי-בינוי?
17. מחיר
18. מחיר למטר
19. שכירות צפויה
20. תשואת שכירות
21. שכירות 3% תשואה
22. predicted price
23. Predicted-Actual
24. Price rank
25. price/size rank
26. yield rank
27. Prediced- actual rank
28. Score

### Sample Formulas:
- G2: =('Data Table'!$F2="חדש מקבלן")*1
- H2: =IF(F2="דרוש שיפוץ",0,
IF(F2="שמור",1,
IF(F2="משופץ",2,
IF(F2="חדש גרו בנכס",3,
IF(F2="חדש מקבלן",4,
- R2: =Q2/(I2+(M2/2))
- T2: =(S2*12)/Q2
- U2: =3%/12*Q2

---

## Sheet: Data Table copy only new

- **Dimensions:** 18 rows × 28 columns
- **Purpose:** (See analysis below)

### Column Names:
1. ID
2. לינק
3. עיר
4. שכונה
5. רחוב
6. מצב הדירה
7. חדשה מקבלן?
8. דירוג מצב הדירה
9. גודל דירה (מר)
10. מספר חדרים
11. קומה
12. מעלית
13. גודל מרפסת (מר)
14. ממד
15. חניה
16. פינוי-בינוי?
17. מחיר
18. מחיר למטר
19. שכירות צפויה
20. תשואת שכירות
21. שכירות 3% תשואה
22. predicted price
23. Predicted-Actual
24. Price rank
25. price/size rank
26. yield rank
27. Prediced- actual rank
28. Score

### Sample Formulas:
- G2: =('Data Table copy only new'!$F2="חדש מקבלן")*1
- H2: =IF(F2="דרוש שיפוץ",0,
IF(F2="שמור",1,
IF(F2="משופץ",2,
IF(F2="חדש גרו בנכס",3,
IF(F2="חדש מקבלן",4,
- R2: =Q2/(I2+(M2/2))
- T2: =(S2*12)/Q2
- U2: =3%/12*Q2

---

## Sheet: Regression

- **Dimensions:** 88 rows × 9 columns
- **Purpose:** (See analysis below)

### Column Names:
1. SUMMARY OUTPUT
2. Unnamed: 1
3. Unnamed: 2
4. Unnamed: 3
5. Unnamed: 4
6. Unnamed: 5
7. Unnamed: 6
8. Unnamed: 7
9. Unnamed: 8

### Sample Formulas:

---

## Sheet: מערכת מידע נדלן - זבוטינסקי רשי

- **Dimensions:** 51 rows × 12 columns
- **Purpose:** (See analysis below)

### Column Names:
1. מערכת מידע נדלן
2. Unnamed: 1
3. Unnamed: 2
4. Unnamed: 3
5. Unnamed: 4
6. Unnamed: 5
7. Unnamed: 6
8. Unnamed: 7
9. Unnamed: 8
10. Unnamed: 9
11. Unnamed: 10
12. Unnamed: 11

### Sample Formulas:

---

## Sheet: Scenarios Calculator

- **Dimensions:** 90 rows × 8 columns
- **Purpose:** (See analysis below)

### Column Names:
1. Unnamed: 0
2. A
3. B
4. C
5. Unnamed: 4
6. Unnamed: 5
7. Unnamed: 6
8. Unnamed: 7

### Sample Formulas:
- C3: =B3
- D3: =B3
- C4: =$B$4
- D4: =$B$4
- C5: =$B$5

---

## Sheet: ציר זמן

- **Dimensions:** 367 rows × 25 columns
- **Purpose:** (See analysis below)

### Column Names:
1. תרחיש
2. A
3. Unnamed: 2
4. Unnamed: 3
5. Unnamed: 4
6. Unnamed: 5
7. Unnamed: 6
8. Unnamed: 7
9. Unnamed: 8
10. Unnamed: 9
11. Unnamed: 10
12. Unnamed: 11
13. Unnamed: 12
14. Unnamed: 13
15. Unnamed: 14
16. Unnamed: 15
17. Unnamed: 16
18. Unnamed: 17
19. Unnamed: 18
20. כן
21. Unnamed: 20
22. Unnamed: 21
23. Unnamed: 22
24. Unnamed: 23
25. Unnamed: 24

### Sample Formulas:
- B2: <openpyxl.worksheet.formula.ArrayFormula object at 0x0000018223BECF20>
- B3: <openpyxl.worksheet.formula.ArrayFormula object at 0x0000018223F909B0>
- B4: <openpyxl.worksheet.formula.ArrayFormula object at 0x0000018223FDB830>
- B5: <openpyxl.worksheet.formula.ArrayFormula object at 0x0000018224019B20>

---

