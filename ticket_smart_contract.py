from pyteal import *


def approval_program():


    on_create = Seq(
        on_create_sale_begin = Btio(Txn.application_args[0]),
        on_create_sale_end = Btoi(Txn.application_args[1]),
        on_create_event_start = Btoi(Txn.application_args[2]),
        on_create_price = Btoi(Txn.application_args[3]),
        [
            App.globalPut( Bytes("Creator"), Txn.sender() ),
            App.globalPut( Bytes("Sale Begin"), on_create_sale_begin ),
            App.globalPut( Bytes("Sale End"), on_create_sale_end ),
            App.globalPut( Bytes("Event Start"), on_create_event_start ),
            App.globalPut( Bytes("Price"), on_create_price ),
            App.globalPut( Bytes("Event Name"), Txn.application_args[4] ),
            App.globalPut( Bytes("Location"), Txn.application_args[5] ),
            App.globalPut( Bytes("Amount"), Txn.application_args[6] ),
            Assert(
                And(
                    Global.latest_timestamp() < on_create_sale_begin,
                    on_create_sale_begin < on_create_sale_end,
                    on_create_sale_begin < on_create_event_start
                ),
            ),
            Return( Int(1) ),
        ]
    )

    is_creator = Txn.sender() == App.globalGet( Bytes("Creator") )


    delete_application = Seq(

        [
            Assert(is_creator == Int(1) ),
            Return(Int(1)),
        ]
    )

    update_application = Seq(

        [
            Assert(is_creator == Int(1) ),
            Return(Int(1)),
        ]
    )

    on_closeout = Seq(

        Return(Int(1))
    )

    on_opt_in = Seq(

        Return(Int(1))
    )


    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.DeleteApplication, delete_application],
        [Txn.on_completion() == OnComplete.UpdateApplication, update_application],
        [Txn.on_completion() == OnComplete.CloseOut, on_closeout],
        [Txn.on_completion() == OnComplete.OptIn, on_opt_in],
    )

    return program


def clear_state_program():

    return Int(1)


if __name__ == "__main__":
    with open("tickets_approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("tickets_clear_state.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=5)
        f.write(compiled)
