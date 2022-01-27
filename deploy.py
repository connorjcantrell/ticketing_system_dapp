import base64
import datetime
import os

from algosdk.future import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod
from pyteal import compileTeal, Mode
from helpers import *
from ticket_smart_contract import approval_program, clear_state_program

def init():
    # user declared account mnemonics
    mnemonic = os.environ.get("MNEMONIC")
    address = os.environ.get("PUBLIC_KEY")
    if mnemonic == None:
        print("Could not find $MNEMONIC envirionment variable")
        return
    if address == None:
        print("Could not find $PUBLIC_KEY envirionment variable")
        return
    
    # define private keys
    creator_private_key = get_private_key_from_mnemonic(mnemonic)       

    # user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config
    algod_address = "http://localhost:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    
    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address)
    
    account_info = algod_client.account_info(address)
    print("Account balance: {} microAlgos".format(account_info.get('amount')))
    if account_info.get('amount') < 1000:
        print("Please add funds before continuing")
        return

    # declare application state storage (immutable)
    local_ints = 0
    local_bytes = 0
    global_ints = 10
    global_bytes = 10
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)
    
    
    # get PyTeal approval program
    approval_program_ast = approval_program()
    # compile program to TEAL assembly
    approval_program_teal = compileTeal(
        approval_program_ast, mode=Mode.Application, version=5
    )
    # compile program to binary
    approval_program_compiled = compile_program(algod_client, approval_program_teal)
    
    
    
    # get PyTeal clear state program
    clear_state_program_ast = clear_state_program()
    # compile program to TEAL assembly
    clear_state_program_teal = compileTeal(
        clear_state_program_ast, mode=Mode.Application, version=5
    )
    # compile program to binary
    clear_state_program_compiled = compile_program(
        algod_client, clear_state_program_teal
    )
    
    
    # create list of bytes for app args
    # TODO: Define arguments
    app_args = []

    # create new application
    app_id = create_app(
        algod_client,
        creator_private_key,
        approval_program_compiled,
        clear_state_program_compiled,
        global_schema,
        local_schema,
        app_args,
    )
    
    # read global state of application
    print(
        "Global state:",
        read_global_state(
            algod_client, account.address_from_private_key(creator_private_key), app_id
        ),
    )
    return

if __name__ == "__main__":
    init()

