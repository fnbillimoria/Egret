#  ___________________________________________________________________________
#
#  EGRET: Electrical Grid Research and Engineering Tools
#  Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC
#  (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
#  Government retains certain rights in this software.
#  This software is distributed under the Revised BSD License.
#  ___________________________________________________________________________

"""
This module contains several helper functions that are useful when
working with transmission models
"""

import egret.model_library.transmission.tx_calc as tx_calc


def dicts_of_vr_vj(buses):
    """
    Create dictionaries of vr and vj values from the bus vm and va values
    """
    # TODO: Change api to be vr_vj_dicts_from_vm_va(bus_vm, bus_va)
    vr = dict()
    vj = dict()
    for bus_name, bus in buses.items():
        vr[bus_name] = tx_calc.calculate_vr_from_vm_va(bus['vm'], bus['va'])
        vj[bus_name] = tx_calc.calculate_vj_from_vm_va(bus['vm'], bus['va'])

    return vr, vj


def dict_of_bus_loads(buses, loads):
    """
    Create dictionaries of the p and q bus load values from the
    load elements
    """
    # loop over all the load elements and sum the loads at each of the buses
    # TODO: Make this dictionary so that it returns None when no load
    bus_p_loads = {k: 0 for k in buses.keys()}
    bus_q_loads = {k: 0 for k in buses.keys()}

    for load_name, load in loads.items():
        bus_name = load['bus']
        bus_p_loads[bus_name] += load['p_load']
        bus_q_loads[bus_name] += load['q_load']

    return bus_p_loads, bus_q_loads


def dict_of_bus_fixed_shunts(buses, shunts):
    """
    Create dictionaries of the p and q bus shunt values from the
    shunt elements
    """
    # loop over all the load elements and sum the loads at each of the buses
    # TODO: Make this dictionary so that it returns None when no shunt
    bus_bs_fixed_shunts = {k: 0 for k in buses.keys()}
    bus_gs_fixed_shunts = {k: 0 for k in buses.keys()}

    for shunt_name, shunt in shunts.items():
        if shunt['shunt_type'] == 'fixed':
            bus_name = shunt['bus']
            if shunt['bs'] != 0.0:
                bus_bs_fixed_shunts[bus_name] += shunt['bs']
            if shunt['gs'] != 0.0:
                bus_gs_fixed_shunts[bus_name] += shunt['gs']

    return bus_bs_fixed_shunts, bus_gs_fixed_shunts

def dict_of_branch_currents(branches, buses):
    """
    Create a dictionary of the branch currents
    (with subkeys ifr, ifj, itr, itj)
    """
    branch_currents = dict()
    branch_currents['ifr'] = dict()
    branch_currents['ifj'] = dict()
    branch_currents['itr'] = dict()
    branch_currents['itj'] = dict()
    for branch_name, branch in branches.items():
        from_bus = buses[branch['from_bus']]
        to_bus = buses[branch['to_bus']]
        ifr = 0
        ifj = 0
        itr = 0
        itj = 0
        if branch['in_service'] \
            and from_bus['vm'] is not None and from_bus['va'] is not None \
            and to_bus['vm'] is not None and to_bus['va'] is not None:
            # we have all the information we need
            y_matrix = tx_calc.calculate_y_matrix_from_branch(branch)
            vfr = tx_calc.calculate_vr_from_vm_va(from_bus['vm'], from_bus['va'])
            vfj = tx_calc.calculate_vj_from_vm_va(from_bus['vm'], from_bus['va'])
            vtr = tx_calc.calculate_vr_from_vm_va(to_bus['vm'], to_bus['va'])
            vtj = tx_calc.calculate_vj_from_vm_va(to_bus['vm'], to_bus['va'])
            ifr = tx_calc.calculate_ifr(vfr, vfj, vtr, vtj, y_matrix)
            ifj = tx_calc.calculate_ifj(vfr, vfj, vtr, vtj, y_matrix)
            itr = tx_calc.calculate_itr(vfr, vfj, vtr, vtj, y_matrix)
            itj = tx_calc.calculate_itj(vfr, vfj, vtr, vtj, y_matrix)
        branch_currents['ifr'][branch_name] = ifr
        branch_currents['ifj'][branch_name] = ifj
        branch_currents['itr'][branch_name] = itr
        branch_currents['itj'][branch_name] = itj
    return branch_currents


def dict_of_branch_powers(branches, buses):
    """
    Create a dictionary of the branch powers
    (with subkeys pf, qf, pt, qt)
    """
    branch_powers = dict()
    branch_powers['pf'] = dict()
    branch_powers['qf'] = dict()
    branch_powers['pt'] = dict()
    branch_powers['qt'] = dict()
    for branch_name, branch in branches.items():
        from_bus = buses[branch['from_bus']]
        to_bus = buses[branch['to_bus']]
        pf = 0
        qf = 0
        pt = 0
        qt = 0
        if branch['in_service'] \
            and from_bus['vm'] is not None and from_bus['va'] is not None \
            and to_bus['vm'] is not None and to_bus['va'] is not None:
            # we have all the information we need
            y_matrix = tx_calc.calculate_y_matrix_from_branch(branch)
            vfr = tx_calc.calculate_vr_from_vm_va(from_bus['vm'], from_bus['va'])
            vfj = tx_calc.calculate_vj_from_vm_va(from_bus['vm'], from_bus['va'])
            vtr = tx_calc.calculate_vr_from_vm_va(to_bus['vm'], to_bus['va'])
            vtj = tx_calc.calculate_vj_from_vm_va(to_bus['vm'], to_bus['va'])
            ifr = tx_calc.calculate_ifr(vfr, vfj, vtr, vtj, y_matrix)
            ifj = tx_calc.calculate_ifj(vfr, vfj, vtr, vtj, y_matrix)
            itr = tx_calc.calculate_itr(vfr, vfj, vtr, vtj, y_matrix)
            itj = tx_calc.calculate_itj(vfr, vfj, vtr, vtj, y_matrix)
            pf = tx_calc.calculate_p(ifr, ifj, vfr, vfj)
            qf = tx_calc.calculate_q(ifr, ifj, vfr, vfj)
            pt = tx_calc.calculate_p(itr, itj, vtr, vtj)
            qt = tx_calc.calculate_q(itr, itj, vtr, vtj)
        branch_powers['pf'][branch_name] = pf
        branch_powers['qf'][branch_name] = qf
        branch_powers['pt'][branch_name] = pt
        branch_powers['qt'][branch_name] = qt
    return branch_powers


def inlet_outlet_branches_by_bus(branches, buses):
    """
    Return dictionaries of the inlet and outlet branches
    to each bus
    """
    inlet_branches_by_bus = {k: list() for k in buses.keys()}
    outlet_branches_by_bus ={k: list() for k in buses.keys()}

    for branch_name, branch in branches.items():
        inlet_branches_by_bus[branch['to_bus']].append(branch_name)
        outlet_branches_by_bus[branch['from_bus']].append(branch_name)

    return inlet_branches_by_bus, outlet_branches_by_bus


def gens_by_bus(buses, gens):
    """
    Return a dictionary of the generators attached to each bus
    """
    gens_by_bus = {k: list() for k in buses.keys()}
    for gen_name, gen in gens.items():
        gens_by_bus[gen['bus']].append(gen_name)

    return gens_by_bus


## attributes which are scaled for power flow models
scaled_attributes = {
                         ('element_type','generator'): [
                                                          'p_min',
                                                          'p_max',
                                                          'q_min',
                                                          'q_max',
                                                          'p_cost',
                                                          'q_cost',
                                                          'startup_capacity',
                                                          'shutdown_capacity',
                                                          'ramp_up_60min',
                                                          'ramp_down_60min',
                                                          'initial_p_output',
                                                          'initial_q_output',
                                                          'pc1',
                                                          'pc2',
                                                          'qc1_min',
                                                          'qc1_max',
                                                          'qc2_min',
                                                          'qc2_max',
                                                          'ramp_agc',
                                                          'ramp_10',
                                                          'ramp_30',
                                                          'ramp_q',
                                                          'power_factor',
                                                          'pg',
                                                          'qg',
                                                       ],
                       ('element_type','storage'): [
                                                        'energy_capacity',
                                                        'max_discharge_rate',
                                                        'min_discharge_rate',
                                                        'max_charge_rate',
                                                        'min_charge_rate',
                                                        'ramp_up_input_60min',
                                                        'ramp_down_input_60min',
                                                        'ramp_up_output_60min',
                                                        'ramp_down_output_60min',
                                                       ],
                       ('element_type','load') : [
                                                      'p_load',
                                                      'q_load',
                                                     ],
                       ('element_type','branch') : [
                                                       'rating_long_term',
                                                        'rating_short_term',
                                                        'rating_emergency',
                                                        ],
                       ('element_type', 'shunt') : [
                                                      'bs',
                                                      'gs',
                                                      'bs_min',
                                                      'bs_max',
                                                      'gs_min',
                                                      'gs_max',
                                                     ],
                       ('element_type', 'area') : [
                                                        'spinning_reserve_requirement',
                                                        'regulation_up_requirement',
                                                        'regulation_down_requirement',
                                                        'flexible_ramp_up_requirement',
                                                        'flexible_ramp_down_requirement',
                                                      ],  
                       ('system_attributes', None ) : [
                                                        'spinning_reserve_requirement',
                                                        'regulation_up_requirement',
                                                        'regulation_down_requirement',
                                                        'flexible_ramp_up_requirement',
                                                        'flexible_ramp_down_requirement',
                                                     ],
                   }


def scale_ModelData_to_pu(model_data):
    return _convert_modeldata_pu(model_data, _divide_by_baseMVA)


def unscale_ModelData_to_pu(model_data):
    return _convert_modeldata_pu(model_data, _multiply_by_baseMVA)


def _multiply_by_baseMVA(element, attr_name, attr, baseMVA):
    _divide_by_baseMVA(element, attr_name, attr, 1./baseMVA)


def _divide_by_baseMVA(element, attr_name, attr, baseMVA):
    if attr is None:
        return
    if isinstance(attr, dict):
        if 'data_type' in attr and attr['data_type'] == 'time_series':
            values_dict = attr['values']
            for time, value in values_dict.items():
                values_dict[time] = value / baseMVA
        elif 'data_type' in attr and attr['data_type'] == 'cost_curve':
            if attr['cost_curve_type'] == 'polynomial':
                values_dict = attr['values']
                new_values = dict()
                for power, coeff in values_dict.items():
                    new_values[int(power)] = coeff*baseMVA**int(power)
                attr['values'] = new_values
            elif attr['cost_curve_type'] == 'piecewise':
                values_list_of_tuples = attr['values']
                new_values = list()
                for point, cost in values_list_of_tuples:
                    new_values.append((point / baseMVA, cost))
                attr['values'] = new_values
    else:
        element[attr_name] = attr / baseMVA


## NOTE: ideally this would be done in the definitions of
##       these constraints. Futher, it is not obvious that
##       the baseMVA provides the best scaling
def _convert_modeldata_pu(model_data, transform_func):

    md = model_data.clone()
    baseMVA = float(md.data['system']['baseMVA'])

    for (attr_type, element_type), attributes in scaled_attributes.items():

        if attr_type == 'system_attributes':
            system_dict = md.data['system']
            for name, sys_attr in system_dict.items():
                if name in attributes:
                    transform_func(system_dict, name, sys_attr, baseMVA)
        
        elif attr_type == 'element_type':
            if element_type not in md.data['elements']:
                continue
            element_dict = md.data['elements'][element_type]
            for name, element in element_dict.items():
                for attr_name, attr in element.items():
                    if attr_name in attributes:
                        transform_func(element, attr_name, attr, baseMVA)

    return md
