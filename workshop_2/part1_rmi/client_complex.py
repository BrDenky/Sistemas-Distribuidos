# Import libraries
import xmlrpc.client
import random


# Funtion to format complex number
def format_complex(real, imag):
    if imag >= 0:
        return f"{real} + {imag}i"
    else:
        return f"{real} - {abs(imag)}i"

# Function to generate random complex number
def generate_complex():
    real = random.randint(-10, 10)
    imag = random.randint(-10, 10)
    return real, imag

# Server configuration
def main():
    HOST = '172.23.198.18'
    PORT = 12000
    
    # Create a client proxy
    proxy = xmlrpc.client.ServerProxy(f"http://{HOST}:{PORT}/RPC2")
    print("Complex Number Manager - Client")
    
    # Menu
    while True:
        print("\n Select an option:")
        print("1. Add complex numbers")
        print("2. Subtract complex numbers")
        print("3. Multiply complex numbers")
        print("4. Divide complex numbers")
        #print("5. Automatic test with random numbers")
        print("6. Exit")
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == '6':
            print("Exiting... Goodbye!")
            break
        
        # if choice == '5':
        #     print("AUTOMATIC TEST WITH RANDOM NUMBERS")
            
        #     # We call to generate two random complex numbers function
        #     real1, imag1 = generate_complex()
        #     real2, imag2 = generate_complex()
            
        #     # We call to format complex number function
        #     c1_str = format_complex(real1, imag1)
        #     c2_str = format_complex(real2, imag2)
            
        #     print(f"\nComplex Number 1: {c1_str}")
        #     print(f"Complex Number 2: {c2_str}")
            
        #     # We call to test all operations
        #     operations = [
        #         ('Addition', 'add'),
        #         ('Subtraction', 'sub'),
        #         ('Multiplication', 'prod'),
        #         ('Division', 'div')
        #     ]
            
        #     for op_name, op_func in operations:
        #         try:
        #             result = getattr(proxy, op_func)(real1, imag1, real2, imag2)
        #             if isinstance(result, str):
        #                 print(f"\n{op_name}: {result}")
        #             else:
        #                 result_str = format_complex(result[0], result[1])
        #                 print(f"\n{op_name}: {result_str}")
        #         except Exception as e:
        #             print(f"\n{op_name} Error: {e}")
            
        #     continue
        
        # Manage invalid choices
        if choice not in ['1', '2', '3', '4']:
            print("Invalid choice. Please try again.")
            continue
        
        # Get manual or random input method
        print("\nInput method:")
        print("1. Manual input")
        print("2. Random generation")
        input_method = input("Choose (1-2): ")
        
        # Manage Error
        if input_method not in ['1', '2']:
            print("Invalid input method. Please try again.")
            continue
        
        # Case 1 - Manual input
        if input_method == '1':
            try:
                print("\nEnter first complex number (a + bi):")
                real1 = float(input("  Real part (a): "))
                imag1 = float(input("  Imaginary part (b): "))
                
                print("\nEnter second complex number (c + di):")
                real2 = float(input("  Real part (c): "))
                imag2 = float(input("  Imaginary part (d): "))
            except ValueError:
                print("Invalid input. Please enter numeric values.")
                continue
        else:
            # Case 2 - Random generation
            real1, imag1 = generate_complex()
            real2, imag2 = generate_complex()
        


        # Display the complex numbers
        c1_str = format_complex(real1, imag1)
        c2_str = format_complex(real2, imag2)
        print(f"\nComplex Number 1: {c1_str}")
        print(f"Complex Number 2: {c2_str}")
        
        # Call the appropriate remote method
        try:
            if choice == '1':
                result = proxy.add(real1, imag1, real2, imag2)
                operation = "Addition"
            elif choice == '2':
                result = proxy.sub(real1, imag1, real2, imag2)
                operation = "Subtraction"
            elif choice == '3':
                result = proxy.prod(real1, imag1, real2, imag2)
                operation = "Multiplication"
            elif choice == '4':
                result = proxy.div(real1, imag1, real2, imag2)
                operation = "Division"
            
            # Display result
            if isinstance(result, str):
                print(f"\n{operation} Result: {result}")
            else:
                result_str = format_complex(result[0], result[1])
                print(f"\n{operation} Result: {result_str}")
        
        except Exception as e:
            print(f"Error calling remote method: {e}")

if __name__ == "__main__":
    main()
