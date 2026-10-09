/**
 * DataTable Component
 * A reusable, generic data table component with sorting, pagination, and filtering capabilities.
 */

import React, { useState, useMemo, useCallback } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown, Search } from 'lucide-react';

interface Column<T> {
  key: string;
  header: string;
  sortable?: boolean;
  render?: (item: T, index: number) => React.ReactNode;
  className?: string;
  width?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  keyExtractor: (item: T) => string;
  itemsPerPage?: number;
  showPagination?: boolean;
  showSearch?: boolean;
  searchKeys?: string[];
  searchPlaceholder?: string;
  emptyMessage?: string;
  className?: string;
  onRowClick?: (item: T) => void;
  onSort?: (key: string, direction: 'asc' | 'desc') => void;
  isLoading?: boolean;
  onSelectAll?: (selected: boolean) => void;
  onSelectRow?: (item: T, selected: boolean) => void;
  selectedRows?: T[];
}

function DataTable<T>({
  data,
  columns,
  keyExtractor,
  itemsPerPage = 10,
  showPagination = true,
  showSearch = true,
  searchKeys = [],
  searchPlaceholder = 'Search...',
  emptyMessage = 'No data available',
  className = '',
  onRowClick,
  onSort,
  isLoading = false,
  onSelectAll,
  onSelectRow,
  selectedRows = [],
}: DataTableProps<T>) {
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);

  // Filter data based on search term
  const filteredData = useMemo(() => {
    if (!searchTerm || searchKeys.length === 0) return data;

    const lowerSearch = searchTerm.toLowerCase();
    return data.filter((item) => {
      return searchKeys.some((key) => {
        const value = (item as Record<string, unknown>)[key];
        if (value === undefined || value === null) return false;
        return String(value).toLowerCase().includes(lowerSearch);
      });
    });
  }, [data, searchTerm, searchKeys]);

  // Sort data
  const sortedData = useMemo(() => {
    if (!sortConfig) return filteredData;

    const { key, direction } = sortConfig;
    const sorted = [...filteredData];

    sorted.sort((a, b) => {
      const aVal = (a as Record<string, unknown>)[key];
      const bVal = (b as Record<string, unknown>)[key];

      if (aVal === undefined || aVal === null) return 1;
      if (bVal === undefined || bVal === null) return -1;

      const aStr = String(aVal);
      const bStr = String(bVal);

      if (direction === 'asc') {
        return aStr.localeCompare(bStr, undefined, { numeric: true });
      } else {
        return bStr.localeCompare(aStr, undefined, { numeric: true });
      }
    });

    return sorted;
  }, [filteredData, sortConfig]);

  // Pagination
  const totalPages = Math.ceil(sortedData.length / itemsPerPage);
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return sortedData.slice(startIndex, startIndex + itemsPerPage);
  }, [sortedData, currentPage, itemsPerPage]);

  // Select all checkbox state
  const allSelected = useMemo(() => {
    if (selectedRows.length === 0) return false;
    if (paginatedData.length === 0) return false;
    return paginatedData.every((item) =>
      selectedRows.some((selected) => keyExtractor(selected) === keyExtractor(item))
    );
  }, [selectedRows, paginatedData, keyExtractor]);

  const handleSort = useCallback((key: string) => {
    let direction: 'asc' | 'desc' = 'asc';

    if (sortConfig && sortConfig.key === key) {
      direction = sortConfig.direction === 'asc' ? 'desc' : 'asc';
    }

    const newSortConfig = { key, direction };
    setSortConfig(newSortConfig);

    // Call external sort handler if provided
    if (onSort) {
      onSort(key, direction);
    }
  }, [sortConfig, onSort]);

  const handleSelectAll = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.checked;
    if (onSelectAll) {
      onSelectAll(selected);
    }
  }, [onSelectAll]);

  const handleSelectRow = useCallback((item: T, e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.checked;
    if (onSelectRow) {
      onSelectRow(item, selected);
    }
  }, [onSelectRow]);

  const getSortIndicator = (key: string) => {
    if (!sortConfig || sortConfig.key !== key) {
      return <ChevronsUpDown className="w-4 h-4 text-gray-400" />;
    }
    return sortConfig.direction === 'asc' ? (
      <ChevronUp className="w-4 h-4 text-primary-600" />
    ) : (
      <ChevronDown className="w-4 h-4 text-primary-600" />
    );
  };

  const renderSortIcon = (column: Column<T>) => {
    if (!column.sortable) return null;
    return (
      <button
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          handleSort(column.key);
        }}
        className="flex items-center gap-1 hover:text-primary-600 transition-colors"
      >
        {getSortIndicator(column.key)}
      </button>
    );
  };

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1); // Reset to first page on search
  };

  const renderCell = (item: T, column: Column<T>, index: number) => {
    if (column.render) {
      return column.render(item, index);
    }
    const value = (item as Record<string, unknown>)[column.key];
    return value !== undefined && value !== null ? String(value) : '-';
  };

  const hasSelectionFeatures = onSelectAll || onSelectRow;

  if (isLoading) {
    return (
      <div className={`table-container ${className}`}>
        <div className="p-8 text-center">
          <div className="animate-spin rounded-full border-4 border-primary-200 border-t-primary-600 h-12 w-12 mx-auto mb-4" />
          <p className="text-gray-600">Loading data...</p>
        </div>
      </div>
    );
  }

  if (sortedData.length === 0) {
    return (
      <div className={`table-container ${className}`}>
        <div className="p-8 text-center">
          <p className="text-gray-500">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Search */}
      {showSearch && (
        <div className="flex items-center gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder={searchPlaceholder}
              value={searchTerm}
              onChange={handleSearchChange}
              className="form-input pl-10"
            />
          </div>
          {showPagination && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span>
                Showing {(currentPage - 1) * itemsPerPage + 1}-{
                  Math.min(currentPage * itemsPerPage, sortedData.length)
                } of {sortedData.length}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Table */}
      <div className="table-container">
        <table className="table">
          <thead className="table-header">
            <tr>
              {hasSelectionFeatures && (
                <th className="table-header-cell w-12">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={handleSelectAll}
                    onClick={(e) => e.stopPropagation()}
                    className="w-4 h-4"
                  />
                </th>
              )}
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`table-header-cell ${column.className || ''}`}
                  style={{ width: column.width }}
                  onClick={() => column.sortable && handleSort(column.key)}
                >
                  <div className="flex items-center gap-2">
                    <span>{column.header}</span>
                    {renderSortIcon(column)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((item, index) => {
              const key = keyExtractor(item);
              const isSelected = selectedRows.some(
                (selected) => keyExtractor(selected) === key
              );

              return (
                <tr
                  key={key}
                  className={`table-row ${
                    onRowClick ? 'cursor-pointer hover:bg-gray-100' : ''
                  }`}
                  onClick={() => onRowClick && onRowClick(item)}
                >
                  {hasSelectionFeatures && (
                    <td className="table-cell">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => handleSelectRow(item, e)}
                        onClick={(e) => e.stopPropagation()}
                        className="w-4 h-4"
                      />
                    </td>
                  )}
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className={`table-cell ${column.className || ''}`}
                    >
                      {renderCell(item, column, index)}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {showPagination && totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="pagination-btn"
          >
            Previous
          </button>

          <div className="flex items-center gap-1">
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
              let pageNum = i + 1;

              // Show pages around current page
              if (totalPages > 5) {
                if (currentPage > 3) {
                  pageNum = currentPage - 2 + i;
                  if (pageNum > totalPages - 2) {
                    pageNum = totalPages - 2 + i;
                  }
                }
                if (pageNum < 1) pageNum = 1;
                if (pageNum > totalPages) pageNum = totalPages;
              }

              return (
                <button
                  key={pageNum}
                  onClick={() => handlePageChange(pageNum)}
                  className={`pagination-btn ${
                    currentPage === pageNum ? 'active' : ''
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="pagination-btn"
          >
            Next
          </button>
          <span className="pagination-info">
            Page {currentPage} of {totalPages}
          </span>
        </div>
      )}
    </div>
  );
}

export default DataTable;
