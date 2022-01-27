from pyteal import *


def approval_program():
    creator_key = Bytes("creator")
    sale_open_key = Bytes("sale_open")
    sale_close_key = Bytes("sale_close")
    price_key = Bytes("price")
    quantity_key = Bytes("quantity")
    event_name_key = Bytes("event_name")
    location_key = Bytes("location")

    on_create_sale_open = (Btoi(Txn.application_args[0]),)
    on_create_sale_close = (Btoi(Txn.application_args[1]),)
    on_create_price = (Btoi(Txn.application_args[2]),)
    on_create_quantity = (Btoi(Txn.application_args[3]),)
    on_create = Seq(
        [
            App.globalPut(creator_key, Txn.sender()),
            App.globalPut(sale_open_key, on_create_sale_open),
            App.globalPut(sale_close_key, on_create_sale_close),
            App.globalPut(price_key, on_create_price),
            App.globalPut(quantity_key, on_create_quantity),
            App.globalPut(location_key, Txn.application_args[4]),
            App.globalPut(quantity_key, Txn.application_args[5]),
            Assert(
                And(
                    Global.latest_timestamp() < on_create_sale_open,
                    on_create_sale_open < on_create_sale_close,
                ),
            ),
            # TODO: Create tickets equal to `quantity`
            # TODO: Create inner transaction for sale of a ticket
            Return(Int(1)),
        ]
    )

    is_creator = Txn.sender() == App.globalGet(Bytes("creator"))

    delete_application = Seq(
        [
            Assert(is_creator == Int(1)),
            Return(Int(1)),
        ]
    )

    update_application = Seq(
        [
            Assert(is_creator == Int(1)),
            Return(Int(1)),
        ]
    )

    on_closeout = Seq(Return(Int(1)))

    on_opt_in = Seq(Return(Int(1)))

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
