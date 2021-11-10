// File generated ${timestamp} by (c) TYPO ${typo_version}
// Do not update its content out of marked places

${copyright}

#pragma once

// user defined includes - manual changes allowed here
#include <string.h>
// generated code

class ${class_name.UppecaseCamel}
{
    public:
        ${simple_type_constructor}
        
        ${simple_type_setter_and_getter}
        
        // user defined code - XXX manual changes allowed here

        std::string toString() const;
        static TrafficLightColor fromString(const std::string& text);
        
        // generated code
    private:
        ${simple_type_value}
};

// manual changes allowed here

std::string TrafficLightColor::toString() const
{
}

static TrafficLightColor TrafficLightColor::fromString(const std::string& text)
{
}

// end of manual changes
