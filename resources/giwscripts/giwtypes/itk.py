import re

from giwscripts import symbols
from giwscripts.giwtypes import interface


def cppTypeToInt(cppType) -> int:
    # gdb constant, SEE to find another way to access it
    TYPE_CODE_INT = 8
    TYPE_CODE_FLT = 9

    cppTypeStr = str(cppType.strip_typedefs())

    # Integer
    if cppType.code == TYPE_CODE_INT:
        if cppTypeStr.find('unsigned') != -1:
            if cppType.sizeof == 1:
                return symbols.GIW_TYPES_UINT8
            elif cppType.sizeof == 2:
                return symbols.GIW_TYPES_UINT16
        else:
            if cppType.sizeof == 2:
                return symbols.GIW_TYPES_INT16
            elif cppType.sizeof == 4:
                return symbols.GIW_TYPES_INT32
    # Float
    elif cppType.code == TYPE_CODE_FLT:
        if cppType.sizeof == 4:
            return symbols.GIW_TYPES_FLOAT32
        elif cppType.sizeof == 8:
            return symbols.GIW_TYPES_FLOAT64
    raise TypeError


class Mat(interface.TypeInspectorInterface):
    def get_buffer_metadata(self, obj_name, picked_obj, debugger_bridge):
        obj = picked_obj['m_Pointer'].dereference()
        pxType = obj.type.template_argument(0)
        sizes = obj['m_LargestPossibleRegion']['m_Size']['m_InternalArray']
        return {
            'display_name':  obj_name + ' (' + str(picked_obj.type) + ')',
            'pointer': debugger_bridge.get_casted_pointer(str(pxType), obj['m_Buffer']['m_Pointer']['m_ImportPointer']),
            'width': int(sizes[0]),
            'height': int(sizes[1]),
            'channels': 1,
            'type': cppTypeToInt(pxType),
            'row_stride': int(sizes[0]),
            'pixel_layout': 'rgba',
            'transpose_buffer': False
        }

    def is_symbol_observable(self, symbol):
        symbol_type = str(symbol.type.strip_typedefs())
        type_regex = r'^itk::SmartPointer<itk::Image.*>$'
        print('Match: ', re.match(type_regex, symbol_type))
        print('type: ', symbol.type)
        print('type clean: ', symbol_type)
        # print('type code: ', symbol.type.strip_typedefs().code)
        # pxType = symbol.type.template_argument(0).template_argument(0)
        # print('type: ', pxType)
        # print('type clean: ', pxType.strip_typedefs())
        # print('type code: ', pxType.strip_typedefs().code)
        # print('dyntype: ', symbol.dynamic_type)
        return re.match(type_regex, symbol_type) is not None
