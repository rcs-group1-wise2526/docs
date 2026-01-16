```py
system_prompt = (
    "Bu bir kişilik anketidir. \n"
    "Her ifade için 1-5 arası tek bir rakam yazın:\n1 = Kesinlikle katılmıyorum\n2 = Katılmıyorum\n3 = Kararsızım\n4 = Katılıyorum\n5 = Kesinlikle katılıyorum \n"
     "SADECE tek bir rakam yazın (1, 2, 3, 4 veya 5). \n" 
    "Açıklama yapmayın."
)

user_prompt = (
    f"Ben ... biriyim: {item_text}."
)
```