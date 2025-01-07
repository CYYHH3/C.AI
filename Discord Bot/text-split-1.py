import re

def split_text(text, max_length):
    words = text.split(" ")  # 将文本按照空格分割成单词列表
    segments = []  # 存储分割后的文本段落
    current_segment = ''  # 当前正在构建的文本段落
    
    def esc(string):
        blank = re.findall('\s', string)
        
        while blank.count(" ") > 0:
            blank.remove(" ")
            
        return len(blank) + string.count("\\")

    for word in words:
        if len(current_segment) + len(word) + esc(current_segment) + esc(word) < max_length:
            current_segment += word + ' '  # 将单词添加到当前段落
        else:
            segments.append(current_segment.strip())  # 当前段落达到最大长度，添加到结果列表
            current_segment = word + ' '  # 开始构建新的段落
        
        '''print([current_segment])
        print(len(current_segment) + esc(current_segment) + current_segment.count("\\"))
        print("\n")'''

    # 添加最后一个段落
    if current_segment:
        segments.append(current_segment.strip())

    '''print(len(current_segment) + esc(current_segment) + current_segment.count("\\"))
    print("\n")'''

    return segments


# 示例用法
text = "I'll provide you with a basic structure for a C program that can serve as a library borrowing and lending system with an inventory check function. You can expand and modify this code to include more features and functionality as needed.\n\n```c\n#include <stdio.h>\n#include <string.h>\n\n// Define the maximum number of books in the library\n#define MAX_BOOKS 100\n\n// Define a structure to store information about a book\ntypedef struct {\n    int id;\n    char title[100];\n    char author[100];\n    int isBorrowed;\n} Book;\n\n// Declare the library inventory\nBook inventory[MAX_BOOKS];\n\n// Initialize the library inventory\nvoid initLibrary() {\n    // Add books to the inventory\n    // Example: inventory[0] = (Book){1, \"Book Title\", \"Book Author\", 0};\n}\n\n// Function to check the inventory for a specific book\nint checkInventory(int id) {\n    for (int i = 0; i < MAX_BOOKS; i++) {\n        if (inventory[i].id == id) {\n            return i;\n        }\n    }\n    return -1;\n}\n\n// Function to borrow a book\nint borrowBook(int id) {\n    int index = checkInventory(id);\n    if (index != -1 && !inventory[index].isBorrowed) {\n        inventory[index].isBorrowed = 1;\n        return 0;\n    }\n    return -1;\n}\n\n// Function to return a book\nint returnBook(int id) {\n    int index = checkInventory(id);\n    if (index != -1 && inventory[index].isBorrowed) {\n        inventory[index].isBorrowed = 0;\n        return 0;\n    }\n    return -1;\n}\n\nint main() {\n    initLibrary();\n\n    // Example usage:\n    // Borrow book with ID 1\n    if (borrowBook(1) == 0) {\n        printf(\"Book borrowed successfully.\\n\");\n    } else {\n        printf(\"Book not available for borrowing.\\n\");\n    }\n\n    // Return book with ID 1\n    if (returnBook(1) == 0) {\n        printf(\"Book returned successfully.\\n\");\n    } else {\n        printf(\"Book not available for returning.\\n\");\n    }\n\n    return 0;\n}\n```\n\nThis code defines a `Book` structure to store information about a book and an array `inventory` to store the library's collection of books. The `initLibrary` function initializes the library inventory. The `checkInventory` function searches for a book by its ID in the inventory. The `borrowBook` and `returnBook` functions handle the borrowing and returning of books, respectively. The `main` function demonstrates example usage of the borrowing and returning functions."
max_length = 2000
segments = split_text(text, max_length)

# 打印分割后的文本段落
print(segments, len(segments))

for segment in segments:
    print(segment)