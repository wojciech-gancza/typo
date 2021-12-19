#include <string>
#include <vector>
#include <math.h>
#include <iostream>

#include "typo_tools.h"
#include "typo_tools.cpp"
#include "mass.h"
#include "name.h"
#include "card_color.cpp"
#include "access_right.cpp"

size_t passed = 0;
size_t failed = 0;

void checkCloseEnough(double have, double expect, size_t line_number)
{
    double diff_as_percetage = 200 * (have - expect) / (have + expect);
    if (abs(diff_as_percetage) > 0.1)
    {
        std::cout << "Error at line " << line_number << ": " << have << " is not close to " << expect << "\n";
        ++failed;
    }
    else
    {
        ++passed;
    }
}

template <class T, class X> void checkEqual(const T& have, const X& expect, size_t line_number)
{
    if (have != T(expect))
    {
        std::cout << "Error at line " << line_number << ": \"" << have << "\" is not equal to \"" << expect << "\"\n";
        ++failed;
    }
    else
    {
        ++passed;
    }
}


int main()
{
    // test of simple numeric generated type
    Mass m;
    checkCloseEnough(m.getMass(), 0.0, __LINE__);
    m = Mass(320);
    checkCloseEnough(m.getMass(), 320.0, __LINE__);
    m.setMass(43.7);
    checkCloseEnough(m.getMass(), 43.7, __LINE__);
    
    // test of string generated type
    Name n;
    checkEqual(n.getName(), "", __LINE__);
    n = Name("xxx");
    checkEqual(n.getName(), "xxx", __LINE__);
    n.setName("abcd");
    checkEqual(n.getName(), "abcd", __LINE__);

    // test of enum
    CardColor x;
    checkEqual(x.getCardColor(), CardColor::CLUBS, __LINE__);
    x = CardColor(CardColor::HEARTS);
    checkEqual(x.getCardColor(), CardColor::HEARTS, __LINE__);
    x.setCardColor(CardColor::SPADES);
    checkEqual(x.getCardColor(), CardColor::SPADES, __LINE__);
    checkEqual(std::string(x.to_string()), "SPADES", __LINE__);
    x = CardColor::from_string("DIAMONDS");
    checkEqual(x.getCardColor(), CardColor::DIAMONDS, __LINE__);
    
    // test of bitset
    AccessRight a;
    checkEqual(a.getAccessRight(), 0, __LINE__);
    a = AccessRight(AccessRight::READ);
    checkEqual(a.getAccessRight(), AccessRight::READ, __LINE__);
    a.setAccessRight(AccessRight::WRITE | AccessRight::EXECUTE);
    checkEqual(a.getAccessRight(), AccessRight::WRITE | AccessRight::EXECUTE, __LINE__);
    checkEqual(a.to_string(), "WRITE | EXECUTE", __LINE__);
    a = AccessRight::from_string("READ |  WRITE");
    checkEqual(a.getAccessRight(), AccessRight::WRITE | AccessRight::READ, __LINE__);
    a = AccessRight::from_string("EXECUTE");
    checkEqual(a.getAccessRight(), AccessRight::EXECUTE, __LINE__);   
    a = AccessRight::from_string("READ | UNKNOWN");
    checkEqual(int(a.getAccessRight()), int(0), __LINE__);   
    
    // desipay results
    std::cout << "--- PASSED: " << passed << "\n"
              << "--- FAILED: " << failed << "\n";
    return 0;
}