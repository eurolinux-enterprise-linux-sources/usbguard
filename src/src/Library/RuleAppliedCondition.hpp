//
// Copyright (C) 2016 Red Hat, Inc.
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
// Authors: Daniel Kopecek <dkopecek@redhat.com>
//
#pragma once
#include "Typedefs.hpp"
#include "RuleCondition.hpp"
#include "Rule.hpp"
#include <chrono>

namespace usbguard
{
  class RuleAppliedCondition : public RuleConditionBase
  {
  public:
    RuleAppliedCondition(const String& elapsed_time, bool negated = false);
    RuleAppliedCondition(const RuleAppliedCondition& rhs);
    bool update(const Rule& rule);
    RuleConditionBase * clone() const;
  protected:
    static uint64_t stringToSeconds(const String& string);
  private:
    std::chrono::steady_clock::duration _elapsed_time;
  };
} /* namespace usbguard */

