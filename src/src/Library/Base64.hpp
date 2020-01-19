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
#include "Typedefs.hpp"
#include <cstddef>

namespace usbguard
{
  size_t base64EncodedSize(size_t decoded_size);
  size_t base64DecodedSize(size_t encoded_size);

  String base64Encode(const String& value);
  String base64Encode(const uint8_t *buffer, size_t buflen);

  String base64Decode(const String& value);
  size_t base64Decode(const String& value, void *buffer, size_t buflen);
  String base64Decode(const char * const data, const size_t size);
} /* namespace usbguard */

