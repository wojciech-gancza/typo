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
#include "side.cpp"
#include "order.h"
#include "stock_position.h"

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
    Test::Mass m;
    checkCloseEnough(m.getMass(), 0.0, __LINE__);
    m = Test::Mass(320);
    checkCloseEnough(m.getMass(), 320.0, __LINE__);
    m.setMass(43.7);
    checkCloseEnough(m.getMass(), 43.7, __LINE__);
    
    // test of string generated type
    Test::Name n;
    checkEqual(n.getName(), "", __LINE__);
    n = Test::Name("xxx");
    checkEqual(n.getName(), "xxx", __LINE__);
    n.setName("abcd");
    checkEqual(n.getName(), "abcd", __LINE__);

    // test of enum
    Test::CardColor x;
    checkEqual(x.getCardColor(), Test::CardColor::CLUBS, __LINE__);
    x = Test::CardColor(Test::CardColor::HEARTS);
    checkEqual(x.getCardColor(), Test::CardColor::HEARTS, __LINE__);
    x.setCardColor(Test::CardColor::SPADES);
    checkEqual(x.getCardColor(), Test::CardColor::SPADES, __LINE__);
    checkEqual(std::string(x.to_string()), "SPADES", __LINE__);
    x = Test::CardColor::from_string("DIAMONDS");
    checkEqual(x.getCardColor(), Test::CardColor::DIAMONDS, __LINE__);
    
    // test of bitset
    Test::AccessRight a;
    checkEqual(a.getAccessRight(), 0, __LINE__);
    a = Test::AccessRight(Test::AccessRight::READ);
    checkEqual(a.getAccessRight(), Test::AccessRight::READ, __LINE__);
    a.setAccessRight(Test::AccessRight::WRITE | Test::AccessRight::EXECUTE);
    checkEqual(a.getAccessRight(), Test::AccessRight::WRITE | Test::AccessRight::EXECUTE, __LINE__);
    checkEqual(a.to_string(), "WRITE | EXECUTE", __LINE__);
    a = Test::AccessRight::from_string("READ |  WRITE");
    checkEqual(a.getAccessRight(), Test::AccessRight::WRITE | Test::AccessRight::READ, __LINE__);
    a = Test::AccessRight::from_string("EXECUTE");
    checkEqual(a.getAccessRight(), Test::AccessRight::EXECUTE, __LINE__);   
    a = Test::AccessRight::from_string("READ | UNKNOWN");
    checkEqual(int(a.getAccessRight()), int(0), __LINE__);   
    
    // test of record
    Test::Order ord;
    checkEqual(ord.getAmount(), 0, __LINE__);
    checkEqual(ord.getName(), std::string(""), __LINE__);
    checkEqual(ord.getSide(), Test::Side::BUY, __LINE__);
    ord.setName("IDX");
    ord.setSide(Test::Side::SEL);
    Test::StockPosition stp;
    stp.setAmount(1200);
    stp.setPrice(415.90);
    ord.setFrom(stp);
    checkEqual(ord.getAmount(), 1200, __LINE__);
    checkCloseEnough(ord.getPrice(), 415.9, __LINE__);
    checkEqual(ord.getName(), std::string("IDX"), __LINE__);
    checkEqual(ord.getSide(), Test::Side::SEL, __LINE__);
    ord.setAmount(630);
    ord.setPrice(417.00);
    stp.setFrom(ord);
    checkEqual(stp.getAmount(), 630, __LINE__);
    checkCloseEnough(stp.getPrice(), 417.0, __LINE__);
      
    // desipay results
    std::cout << "--- PASSED: " << passed << "\n"
              << "--- FAILED: " << failed << "\n";
    return 0;
}