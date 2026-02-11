from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# Restrict to a particular path
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Complex number operations
def add_complex(real1, imag1, real2, imag2):
    """Add two complex numbers"""
    result_real = real1 + real2
    result_imag = imag1 + imag2
    return (result_real, result_imag)

def sub_complex(real1, imag1, real2, imag2):
    """Subtract two complex numbers"""
    result_real = real1 - real2
    result_imag = imag1 - imag2
    return (result_real, result_imag)

def prod_complex(real1, imag1, real2, imag2):
    """Multiply two complex numbers: (a+bi)(c+di) = (ac-bd) + (ad+bc)i"""
    result_real = real1 * real2 - imag1 * imag2
    result_imag = real1 * imag2 + imag1 * real2
    return (result_real, result_imag)

def div_complex(real1, imag1, real2, imag2):
    """Divide two complex numbers: (a+bi)/(c+di) = [(ac+bd) + (bc-ad)i] / (c²+d²)"""
    if real2 == 0 and imag2 == 0:
        return "Error: Division by zero"
    
    denominator = real2 * real2 + imag2 * imag2
    result_real = (real1 * real2 + imag1 * imag2) / denominator
    result_imag = (imag1 * real2 - real1 * imag2) / denominator
    return (result_real, result_imag)

# Create server
if __name__ == "__main__":
    HOST = 'localhost'  # Change to '0.0.0.0' for different hosts
    PORT = 12000
    
    with SimpleXMLRPCServer((HOST, PORT),
                            requestHandler=RequestHandler,
                            allow_none=True) as server:
        server.register_introspection_functions()
        
        # Register complex number functions
        server.register_function(add_complex, 'add')
        server.register_function(sub_complex, 'sub')
        server.register_function(prod_complex, 'prod')
        server.register_function(div_complex, 'div')
        
        # Run the server's main loop
        print(f"Complex Number Manager Server listening on {HOST}:{PORT}...")
        print("Available operations: add, sub, prod, div")
        server.serve_forever()
