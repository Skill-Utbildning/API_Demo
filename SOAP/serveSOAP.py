from flask import Flask, request, Response
from zeep import Client, Plugin
from zeep.wsdl.utils import etree_to_string
from lxml import etree
import io

app = Flask(__name__)

# Define the WSDL
wsdl = """
<definitions name="CRUDService"
             targetNamespace="http://example.com/crud"
             xmlns:tns="http://example.com/crud"
             xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema"
             xmlns="http://schemas.xmlsoap.org/wsdl/">

  <message name="CreateRequest">
    <part name="data" type="xsd:string"/>
  </message>
  <message name="CreateResponse">
    <part name="result" type="xsd:string"/>
  </message>

  <portType name="CRUDPortType">
    <operation name="Create">
      <input message="tns:CreateRequest"/>
      <output message="tns:CreateResponse"/>
    </operation>
  </portType>

  <binding name="CRUDBinding" type="tns:CRUDPortType">
    <soap:binding style="rpc" transport="http://schemas.xmlsoap.org/soap/http"/>
    <operation name="Create">
      <soap:operation soapAction="create"/>
      <input>
        <soap:body use="literal"/>
      </input>
      <output>
        <soap:body use="literal"/>
      </output>
    </operation>
  </binding>

  <service name="CRUDService">
    <port name="CRUDPort" binding="tns:CRUDBinding">
      <soap:address location="http://localhost:5000/soap"/>
    </port>
  </service>
</definitions>
"""

# Implement the CRUD operations
class CRUDService:
    def create(self, data):
        return f"Created: {data}"

# SOAP Plugin to handle requests
class MyPlugin(Plugin):
    def ingress(self, envelope, http_headers, operation):
        print("Request:", etree_to_string(envelope))
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        print("Response:", etree_to_string(envelope))
        return envelope, http_headers

# Convert WSDL string to a file-like object
wsdl_file = io.StringIO(wsdl)
client = Client(wsdl=wsdl_file, plugins=[MyPlugin()])

@app.route('/soap', methods=['POST'])
def soap():
    # Log the incoming request
    print("Incoming request data:", request.data)
    
    # Parse the incoming request
    envelope = etree.fromstring(request.data)
    body = envelope.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
    create_request = body.find('{http://example.com/crud}Create')
    data = create_request.find('data').text
    
    # Call the service method
    service = CRUDService()
    result = service.create(data)
    
    # Create the response
    response_envelope = etree.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
    response_body = etree.SubElement(response_envelope, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
    create_response = etree.SubElement(response_body, '{http://example.com/crud}CreateResponse')
    result_element = etree.SubElement(create_response, 'result')
    result_element.text = result
    
    # Convert the response to a string
    response_data = etree.tostring(response_envelope, pretty_print=True)
    
    # Log the outgoing response
    print("Outgoing response data:", response_data)
    
    return Response(response_data, mimetype='text/xml')

if __name__ == '__main__':
    app.run(debug=True)