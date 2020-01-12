#ifndef SYSGROUP_TEST_H
#define SYSGROUP_TEST_H

#include <gtest/gtest.h>
#include <gmock/gmock-matchers.h>
#include "../include/sysgroup.h"

using namespace testing;

#include <string>

TEST(Tests, CREATING)
{
    struct group_test {
        std::string name;
        int G;
        int k;
    };
    group_test groups[] = {
        group_test {
            "Group1",
            2,
            3,
        },
        group_test {
            "Group2",
            -3,
            0,
        },
    };

    for (const group_test &grp : groups) {
        SysGroup group(grp.name, grp.G, grp.k);
        ASSERT_EQ(grp.name, group.getName());
        ASSERT_EQ(grp.G, group.getG());
        ASSERT_EQ(grp.k, group.getK());
    }

}

#endif // SYSGROUP_TEST_H
