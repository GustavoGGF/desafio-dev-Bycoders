from datetime import date, time
from io import BytesIO

from app.schemas import TransacaoBase
from app.parser import parse_cnab_stream as cnab_parser
from typing import BinaryIO, Generator, cast

def test_parse_cnab_valid_line():
    # 1. Arrange
    line = b"120230320000001234512345678901475395125827183000JOAO MACEDO   BAR DO JOAO        "
    file_buffer = cast(BinaryIO, BytesIO(line))
    
    # 2. Act
    # Ao usar o alias 'cnab_parser', o VS Code é forçado a re-checar o tipo
    generator: Generator[TransacaoBase, None, None] = cnab_parser(file_buffer)
    results = list(generator)
    
    assert len(results) == 1
    transacao = results[0]
    
    assert transacao.tipo == 1
    assert transacao.valor == 123.45
    assert transacao.data == date(2023, 3, 20)
    assert transacao.cpf == "12345678901"
    assert transacao.cartao == "475395125827"
    assert transacao.hora == time(18, 30, 0)
    assert transacao.nome_loja == "BAR DO JOAO"

def test_parse_cnab_invalid_value_type():
    # O campo de valor (posição 9 a 19) contém letras em vez de números
    line = b"120230320ABCDEFGHIJ12345678901475395125827183000JOAO MACEDO   BAR DO JOAO        "
    file_buffer = cast(BinaryIO, BytesIO(line))
    
    generator = cnab_parser(file_buffer)
    results = list(generator)
    
    assert len(results) == 0

def test_parse_cnab_line_too_short():
    # Uma linha com apenas 10 caracteres (o layout exige 80)
    line = b"120230320"
    file_buffer = cast(BinaryIO, BytesIO(line))
    
    generator = cnab_parser(file_buffer)
    results = list(generator)
    
    assert len(results) == 0

def test_parse_cnab_invalid_date():
    # Data inexistente: 2023-13-45 (Mês 13, Dia 45)
    line = b"120231345000001234512345678901475395125827183000JOAO MACEDO   BAR DO JOAO        "
    file_buffer = cast(BinaryIO, BytesIO(line))
    
    generator = cnab_parser(file_buffer)
    results = list(generator)
    
    assert len(results) == 0