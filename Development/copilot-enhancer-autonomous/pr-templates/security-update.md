## 🔒 Security: Dependency Update

### Security Advisory
**Severity:** {{ severity }}  
**Package:** {{ package_name }}  
**Affected Version:** {{ current_version }}  
**Fixed Version:** {{ fixed_version }}

### Vulnerability Details
{{ vulnerability_description }}

**CVE:** {{ cve_id }}  
**CVSS Score:** {{ cvss_score }}

### Changes Made
- Updated `{{ package_name }}` from {{ current_version }} to {{ fixed_version }}
- Verified compatibility with existing code
- Ran full test suite

### Impact Assessment
- **Breaking Changes:** {{ breaking_changes }}
- **API Changes:** {{ api_changes }}
- **Migration Required:** {{ migration_required }}

### Testing
- ✅ All tests pass
- ✅ Security scan clean
- ✅ No new vulnerabilities introduced
- ✅ Functionality verified

### Auto-Merge Criteria
- [x] Security patch only
- [x] All tests passing
- [x] No breaking changes
- [x] Vulnerability resolved

---
**Type:** Security Update  
**Risk:** LOW (patch version)  
**Review Required:** No (auto-approved for security patches)
**Security Advisory:** [Link to advisory]
