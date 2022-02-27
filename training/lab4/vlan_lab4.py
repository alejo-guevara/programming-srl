###########################################################################
# Description: CLI plugin for the command 'show vlan'
###########################################################################

from srlinux.mgmt.cli import CliPlugin
from srlinux.syntax import Syntax
from srlinux.schema import FixedSchemaRoot
from srlinux.location import build_path
from srlinux.mgmt.cli import KeyCompleter
from srlinux import strings
from srlinux.data import ColumnFormatter, TagValueFormatter, TagValueWithKeyLineFormatter, Formatter
from srlinux.data import Border, Borders, Data, Indent, Header, Whiteline, Footer, Alignment
from srlinux.syntax.value_checkers import IntegerValueInRangeChecker
from srlinux.data.utilities import Percentage
import json

class CheckInstanceName(object):
    def __call__(self, value) -> bool:
        try:
            if value != 'default':
                raise ValueError()
        except ValueError:
            raise ValueError(f"\nThis command is not supported for network instance '{value}'")
        return True

class Plugin(CliPlugin):
    '''
        Load() method: load new CLI command at CLI startup
        In: cli, the root node of the CLI command hierachy
    '''
    __interface_types = {'l2', 'l3', 'lag', 'bridge'}

    def load(self, cli, **_kwargs):
        ## add your code here
        syntax = Syntax('vlan', help='display all configured vlan(s)')
        syntax.add_unnamed_argument(
                'interface',
                default='*',
                #suggestions=KeyCompleter(path='/interface[name=*]'),
                help='interface name')
        syntax.add_named_argument(
                'vlan-id',
                help='look-up this vlan ID only',
                #value_checker=IntegerValueInRangeChecker(1, 4095),
                default='*')
        syntax.add_named_argument(
                'network-instance',
                help='network instance name',
                #value_checker=CheckInstanceName(),
                #suggestions=KeyCompleter(path='/network-instance[name=*]'),
                default='default')
        syntax.add_named_argument(
                'interface-type',
                default='*',
                #choices=['*'] + list(self.__interface_types),
                help='interface type')
        syntax.add_boolean_argument(
                'show-ip-address',
                help='display primary IP addresses')

        print("Loading CLI:", syntax) ## temporary display

        cli.show_mode.add_command(
                syntax,
                update_location=False,
                callback=self._print,
                schema=self._my_schema()
        )

    '''
        _my_schema() method: contruct schema for this CLI command
        Return: schema object
    '''

    def _my_schema(self):
        root = FixedSchemaRoot()

        interface = root.add_child(
               'interface',
                key='name',
                fields=['description', 'vlan-tagging'])

        subint = interface.add_child(
                'subinterface',
                key='name',
                fields=['vlan-id', 'ipv4-address', 'ipv6-address'])

        return root
    '''
        _fetch_state() method: extract relevant data from the state datastore
        In: state, reference to the datastores
        In: arguments, the CLI command's context
        Return: copy of a section of the state datastore
    '''
    def _fetch_state(self, state, arguments):

        ## build a YANG path objects from the path string
        ## retrieve the interface name from the arguments
        path = build_path('/interface[name={name}]', name=arguments.get('interface'))

        ## fetch the value of the YANG path recursively
        ## this will return everythin under the given interface
        data = state.server_data_store.get_data(path, recursive=True)

        return data
    '''
        _populate_schema() method: fill in schema from state datastore
        In: state_datastore, state datastore extract
        In: arguments, the CLI commands context
        Return: filled-in schema
    '''
    def _populate_schema(self, state_datastore, arguments):

        # retrieve the schema from the input arguments
        schema = Data(arguments.schema)

        # populate it with the relevant data from the state datastore
        for interface in state_datastore.interface.items():
            # if multiple interfaces were retrieved from the state datastore
            # populate each of them only if the oper state is up
            if interface.oper_state == 'up':
                # create a new instance for each interface (key = name)
                intf_node = schema.interface.create(interface.name)
                # and populate the description and vlan_tagging fields
                intf_node.description = interface.description
                intf_node.vlan_tagging = interface.vlan_tagging

                # loop through the subinterfaces from the state datastore
                for subinterface in interface.subinterface.items():

                    # create a new subinterface schema instance
                    subintf_node = intf_node.subinterface.create(subinterface.name)
                    vlan_id_encap = subinterface.vlan.get().encap.get()
                    subintf_node.vlan_id = 'null'
                    # check if the vlan container exists
                    if vlan_id_encap.single_tagged.exists():
                        # if yes, retirved the vlan ID
                        subintf_node.vlan_id = vlan_id_encap.single_tagged.get().vlan_id
                        # check if the IP addresses should be displayed
                        if (arguments.get('show-ip-address')):
                            # look for the ipv4 container
                            if subinterface.ipv4.exists():
                                # if there are multiple IP addresses only take the primary IP
                                for ipv4addr in subinterface.ipv4.get().address.items():
                                    if ( subinterface.ipv4.get().address.count() == 1 or ipv4addr.primary):
                                        subintf_node.ipv4_address =  ipv4addr.ip_prefix
                            # same for IPv6
                            if subinterface.ipv6.exists():
                                for ipv6addr in subinterface.ipv6.get().address.items():
                                    if (subinterface.ipv6.get().address.count() == 1 or ipv6addr.primary):
                                        subintf_node.ipv6_address =  ipv6addr.ip_prefix



        # return the schema with all the interfaces
        return schema    

    '''
        _set_formatters() method
        In: schema, schema to augment with formatters
    '''
    def _set_formatters(self, schema):

        ## Assign a formatter to the 'interface' node
        ##   -> uncomment one of the lines below /interface to test a different formatter
        schema.set_formatter(
            '/interface',
            TagValueFormatter())
            #Header(TagValueFormatter(), "This is the interface header text"))
            #MyInterfaceFormatter())
            #Border(TagValueFormatter(), Border.Above | Border.Below | Border.Between,'='))
            #TagValueWithKeyLineFormatter())

        ## Assign a formatter to the 'subinterface' node
        ##   -> uncomment on of the lines below /interface/subinterface to test a formatter
        schema.set_formatter(
            '/interface/subinterface',
            TagValueFormatter(ancestor_keys=False))
            #ColumnFormatter(ancestor_keys=False, borders=Borders.Outside|Borders.Header, horizontal_alignment={'name': Alignment.Center,'vlan_id': Alignment.Center,'ipv4_address' : Alignment.Center,'ipv6_address' : Alignment.Center},widths=[Percentage(25), Percentage(25), Percentage(25), Percentage(25)]))
            #Indent(Header(TagValueFormatter(),text="Subinterfaces", character='+'), indentation=4))
            #Indent(Border(TagValueWithKeyLineFormatter(), Border.Above | Border.Below ), indentation=4))
            #Whiteline(Indent(ColumnFormatter(ancestor_keys=False, borders=Borders.Header, widths={'Name':18, 'Vlan-id':8, 'ipv4-address': 20}), indentation=4), Whiteline.Above))
            #ColumnFormatter(ancestor_keys=False))
            #Indent(MySubinterfaceFormatter(), indentation=4))
            #Footer(ColumnFormatter(ancestor_keys=False), "this is the subinterface footer text"))

    '''
        _print() method: the callback function
        In: state, reference to the datastores
        In: arguments, the CLI command's context
        In: output: the CLI output object
    '''
    def _print(self, state, arguments, output, **_kwargs):
        print("This is the callback method for 'show vlan'")

        for arg in arguments.all_arguments:
            print(arg, arguments.all_arguments[arg])

        print('interface = ', arguments.get('interface'))
        print('vlan-id = ', arguments.get('vlan-id'))
        print('network-instance = ', arguments.get('network-instance'))
        print('interface-type = ', arguments.get('interface-type'))
        print('show-ip-address = ', arguments.get('show-ip-address'))

        # fetch the relevant data from teh state datastore
        state_datastore = self._fetch_state(state, arguments)
        
        print('child_names', *state_datastore.child_names)
        for child in state_datastore.iter_children():
            print("child", child)
            for field, value in zip(child.field_names, child.field_values):
                print(f"    {field} = {value}")
            for subchild in child.iter_children():
                print("    subchild", subchild)
                for field, value in zip(subchild.field_names, subchild.field_values):
                    print(f"        {field} = {value}")
                if 'subinterface' in str(subchild):
                    print('        subinterface children:')
                    for subsubchild in subchild.child_names:
                        print(f'            {subsubchild}')

        # use the fetched data to populate the schema 
        schema = self._populate_schema(state_datastore, arguments)

        # Assign formatters to the schema nodes
        self._set_formatters(schema)

        # Let the CLI engine display the output based on the schema
        # the schema now contains the date to be displayed
        # and the formatters to tell the CLI engine how to display them

        output.print_data(schema)


######################################################################
#
# Custom formatter 'MyInterfaceFormatter'
#
######################################################################
class MyInterfaceFormatter(Formatter):

    def iter_format(self, entry, max_width):
        nb_subintf = entry.subinterface.count()
        yield f"  The interface {entry.name} has VLAN tagging {'enabled' if entry.vlan_tagging == True else 'disabled'} and has {entry.subinterface.count()} subinterface{'s' if abs(nb_subintf) != 1 else ''}"
        yield from entry.subinterface.iter_format(max_width)


######################################################################
#
# Custom formatter 'MySubinterfaceFormatter'
#
######################################################################
class MySubinterfaceFormatter(Formatter):

    def iter_format(self, entry, max_width):
        str = f"  The subinterface {entry.name} has vlan ID {entry.vlan_id} "
        if entry.ipv4_address != None:
            str = str + f"and IP address {entry.ipv4_address}"
        yield str



