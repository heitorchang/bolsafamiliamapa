# Gerar uma pagina com OpenStreetMap contendo dados de
# http://www.dados.gov.br/dataset/bolsa-familia-misocial
# e dados geograficos de
# ftp://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/localidades

import datetime
import os
import glob
from pykml import parser


class Pagamento:
    # representa um pagamento e a data dela
    def __init__(self, d, v):
        self.data = d
        self.valor = v

    def __str__(self):
        return "{}: {}".format(self.data.strftime("%Y-%m-%d"), self.valor)

    def __repr__(self):
        return str(self)

    
class Municipio:
    # representa o name, lng, lat e serie de pagamentos
    def __init__(self, nome, uf, lng, lat):
        self.nome = nome
        self.uf = uf
        self.lng = lng
        self.lat = lat
        self.pagamentos = []

    def adicionarPagamento(self, d, v):
        self.pagamentos.append(Pagamento(d, v))

    def __str__(self):
        return "{} ({}) ({:.5f}, {:.5f}) [{} pagtos]".format(
            self.nome, self.uf, self.lng, self.lat,
            len(self.pagamentos)
        )

    def __repr__(self):
        return str(self)

    
def main():
    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    except NameError:
        data_dir = "c:/Users/heitor/Desktop/code/bolsafamiliamapa/data/"
    kml_file = os.path.join(data_dir, "locone.kml")

    municipios = {}
    
    # process kml
    parse_kml_data(kml_file, municipios)

    print(municipios)
    
    # Bolsa Familia
    pbf_dir = os.path.join(data_dir, "pbf")

    os.chdir(pbf_dir)
    for f in glob.glob('*'):
        print(f)


def parse_kml_data(kml_file, municipios):
    with open(kml_file, encoding="utf-8") as f:
        doc = parser.parse(f)        
        folder = doc.getroot().Document.Folder

        for p in folder.Placemark:
            nome = p.name.text.title()
            simpledata = p.ExtendedData.SchemaData.SimpleData
            for sd in simpledata:
                print(sd)
                if sd.attrib['name'] == "CD_GEOCODMU":
                    codigo_ibge = sd.text[:6]
                elif sd.attrib['name'] == "NM_UF":
                    uf = sd.text.title()
                elif sd.attrib['name'] == "LONG":
                    lng = float(sd.text)
                elif sd.attrib['name'] == "LAT":
                    lat = float(sd.text)
            municipios[codigo_ibge] = Municipio(nome, uf, lng, lat)
                    
    
if __name__ == '__main__':
    print("Generating SPA")
    main()
